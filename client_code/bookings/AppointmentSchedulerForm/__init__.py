from ._anvil_designer import AppointmentSchedulerFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime, timedelta

class AppointmentSchedulerForm(AppointmentSchedulerFormTemplate):
  def __init__(self, **properties):
    self.selected_service = None
    self.selected_time = None
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "Schedule Appointment"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True
    self.lbl_title.role = "headline"

    # Configure field labels
    self.lbl_client_field.text = "Client *"
    self.lbl_client_field.bold = True

    self.lbl_service_field.text = "Service *"
    self.lbl_service_field.bold = True

    self.lbl_staff_field.text = "Staff Member"
    self.lbl_staff_field.bold = True

    self.lbl_meeting_type_field.text = "Meeting Type *"
    self.lbl_meeting_type_field.bold = True

    self.lbl_date_field.text = "Date *"
    self.lbl_date_field.bold = True

    self.lbl_timeslots_field.text = "Available Time Slots:"
    self.lbl_timeslots_field.bold = True

    self.lbl_notes_field.text = "Client Notes"
    self.lbl_notes_field.bold = True

    # Configure client dropdown
    self.dd_client.placeholder = "Search or select client..."
    self.load_clients()

    # Configure service dropdown
    self.dd_service.placeholder = "Select service..."
    self.load_services()

    # Configure service info label
    self.lbl_service_info.visible = False
    self.lbl_service_info.foreground = "#666666"

    # Configure staff dropdown
    self.dd_staff.placeholder = "Select staff member..."
    self.dd_staff.enabled = False  # Enable after service selected

    # Configure meeting type radio buttons
    self.rb_in_person.text = "In-Person"
    self.rb_in_person.group_name = "meeting_type"
    self.rb_in_person.selected = True

    self.rb_video.text = "Video Call"
    self.rb_video.group_name = "meeting_type"

    self.rb_phone.text = "Phone"
    self.rb_phone.group_name = "meeting_type"

    # Configure date picker
    self.dp_date.date = datetime.now().date() + timedelta(days=1)

    # Configure timeslots
    self.rp_timeslots.item_template = 'bookings.TimeSlotRadioTemplate'
    self.rp_timeslots.visible = False

    # Configure notes
    self.txt_notes.placeholder = "Any preparation needed, concerns, etc..."
    self.txt_notes.rows = 3

    # Configure message
    self.lbl_message.visible = False
    self.lbl_message.align = "center"

    # Configure buttons
    self.btn_cancel.text = "Cancel"
    self.btn_cancel.role = "secondary-color"

    self.btn_schedule.text = "Schedule Appointment"
    self.btn_schedule.icon = "fa:calendar-check"
    self.btn_schedule.role = "primary-color"

  def load_clients(self):
    """Load client list"""
    try:
      clients = anvil.server.call('get_all_customers')
      self.dd_client.items = [
        (c['email'], c.get_id()) for c in clients
      ]
    except Exception as e:
      print(f"Error loading clients: {e}")

  def load_services(self):
    """Load services list"""
    try:
      services = anvil.server.call('get_all_services')
      self.dd_service.items = [
        (s['service_name'], s.get_id()) for s in services
      ]
    except Exception as e:
      print(f"Error loading services: {e}")

  def dropdown_service_change(self, **event_args):
    """Load service details and staff"""
    service_id = self.dd_service.selected_value
    if service_id:
      try:
        self.selected_service = anvil.server.call('get_service', service_id)

        # Display service info
        duration = self.selected_service['duration_minutes']
        price = self.selected_service['price']
        self.lbl_service_info.text = f"Duration: {duration} minutes  •  Price: ${price:.2f}"
        self.lbl_service_info.visible = True

        # Load staff for this service
        if self.selected_service.get('staff_id'):
          # Service assigned to specific staff
          self.dd_staff.items = [(
            self.selected_service['staff_id']['email'].split('@')[0],
            self.selected_service['staff_id'].get_id()
          )]
          self.dd_staff.selected_value = self.selected_service['staff_id'].get_id()
          self.dd_staff.enabled = False
        else:
          # Load all staff
          staff = anvil.server.call('get_staff_members')
          self.dd_staff.items = [
            (s['email'].split('@')[0], s.get_id()) for s in staff
          ]
          self.dd_staff.enabled = True

        # Reload timeslots if date already selected
        if self.dp_date.date:
          self.load_timeslots()

      except Exception as e:
        alert(f"Error loading service: {str(e)}")

  def datepicker_date_change(self, **event_args):
    """Load available timeslots when date changes"""
    if self.selected_service:
      self.load_timeslots()

  def load_timeslots(self):
    """Load available time slots"""
    if not self.selected_service or not self.dp_date.date:
      return

    try:
      staff_id = self.dd_staff.selected_value
      date = self.dp_date.date
      duration = self.selected_service['duration_minutes']

      slots = anvil.server.call(
        'get_available_appointment_slots',
        staff_id,
        date,
        duration
      )

      if slots:
        self.rp_timeslots.items = slots
        self.rp_timeslots.visible = True
      else:
        self.rp_timeslots.visible = False
        self.show_message("No available slots for this date", "warning")

    except Exception as e:
      alert(f"Error loading timeslots: {str(e)}")

  def timeslot_selected(self, time_slot):
    """Called by TimeSlotRadioTemplate when time selected"""
    self.selected_time = time_slot

  def button_schedule_click(self, **event_args):
    """Schedule the appointment"""
    try:
      self.lbl_message.visible = False

      # Validate
      if not self.dd_client.selected_value:
        self.show_message("Client is required", "warning")
        return

      if not self.dd_service.selected_value:
        self.show_message("Service is required", "warning")
        return

      if not self.dp_date.date:
        self.show_message("Date is required", "warning")
        return

      if not self.selected_time:
        self.show_message("Please select a time slot", "warning")
        return

      # Get meeting type
      if self.rb_in_person.selected:
        meeting_type = "In-Person"
      elif self.rb_video.selected:
        meeting_type = "Video Call"
      else:
        meeting_type = "Phone"

      # Parse datetime
      hour, minute = map(int, self.selected_time.split(':'))
      appointment_datetime = datetime.combine(
        self.dp_date.date,
        datetime.min.time()
      ).replace(hour=hour, minute=minute)

      # End time
      end_datetime = appointment_datetime + timedelta(
        minutes=self.selected_service['duration_minutes']
      )

      # Prepare appointment data
      appointment_data = {
        'customer_id': self.dd_client.selected_value,
        'service_id': self.dd_service.selected_value,
        'staff_id': self.dd_staff.selected_value,
        'start_datetime': appointment_datetime,
        'end_datetime': end_datetime,
        'meeting_type': meeting_type,
        'client_notes': self.txt_notes.text,
        'total_amount': self.selected_service['price']
      }

      # Schedule via server
      result = anvil.server.call('schedule_appointment', appointment_data)

      if result['success']:
        Notification("✅ Appointment scheduled successfully!", style="success").show()
        open_form('bookings.BookingListForm')
      else:
        self.show_message(result['error'], "danger")

    except Exception as e:
      self.show_message(f"Error scheduling appointment: {str(e)}", "danger")

  def button_cancel_click(self, **event_args):
    """Cancel and return"""
    open_form('bookings.BookingListForm')

  def show_message(self, text, style):
    """Display message"""
    self.lbl_message.text = text
    self.lbl_message.role = f"alert-{style}"
    self.lbl_message.visible = True

  @handle("dd_client", "change")
  def dd_client_change(self, **event_args):
    """This method is called when an item is selected"""
    pass

  @handle("dd_service", "change")
  def dd_service_change(self, **event_args):
    """This method is called when an item is selected"""
    pass

  @handle("dp_date", "change")
  def dp_date_change(self, **event_args):
    """This method is called when the selected date changes"""
    pass

  @handle("btn_cancel", "click")
  def btn_cancel_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_schedule", "click")
  def btn_schedule_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
