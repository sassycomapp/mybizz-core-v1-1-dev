from ._anvil_designer import PublicBookingWidgetTemplate
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

class PublicBookingWidget(PublicBookingWidgetTemplate):
  def __init__(self, **properties):
    self.selected_date = None
    self.selected_time = None
    self.selected_resource = None
    self.available_slots = []
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "Book an Appointment"
    self.lbl_title.font_size = 24
    self.lbl_title.bold = True
    self.lbl_title.align = "center"
    self.lbl_title.role = "headline"

    # Configure step labels
    self.lbl_step1.text = "STEP 1: Select Service"
    self.lbl_step1.bold = True
    self.lbl_step1.font_size = 14

    self.lbl_step2.text = "STEP 2: Choose Date & Time"
    self.lbl_step2.bold = True
    self.lbl_step2.font_size = 14

    self.lbl_step3.text = "STEP 3: Your Details"
    self.lbl_step3.bold = True
    self.lbl_step3.font_size = 14

    # Configure service dropdown
    self.dd_service.placeholder = "Select service or resource..."
    self.load_services()

    # Configure timeslots repeating panel
    self.rp_timeslots.item_template = 'bookings.TimeSlotTemplate'

    # Configure customer detail fields
    self.txt_name.placeholder = "Your full name"
    self.txt_name.icon = "fa:user"

    self.txt_email.placeholder = "your@email.com"
    self.txt_email.type = "email"
    self.txt_email.icon = "fa:envelope"

    self.txt_phone.placeholder = "Phone number (optional)"
    self.txt_phone.icon = "fa:phone"

    self.txt_notes.placeholder = "Any special requests or notes (optional)"
    self.txt_notes.rows = 3

    # Configure book button
    self.btn_book_now.text = "Book Now"
    self.btn_book_now.icon = "fa:check"
    self.btn_book_now.role = "primary-color"
    self.btn_book_now.enabled = False  # Enable after selections made

    # Configure message label
    self.lbl_message.visible = False
    self.lbl_message.align = "center"

    # Initially hide steps 2 and 3
    self.lbl_step2.visible = False
    self.col_calendar.visible = False
    self.rp_timeslots.visible = False
    self.lbl_step3.visible = False
    self.txt_name.visible = False
    self.txt_email.visible = False
    self.txt_phone.visible = False
    self.txt_notes.visible = False

  def load_services(self):
    """Load available services/resources"""
    try:
      services = anvil.server.call('get_public_bookable_resources')
      self.dd_service.items = [
        (s['resource_name'], s.get_id()) for s in services
      ]
    except Exception as e:
      print(f"Error loading services: {e}")

  def dropdown_service_change(self, **event_args):
    """Show calendar when service selected"""
    self.selected_resource = self.dd_service.selected_value
    if self.selected_resource:
      self.lbl_step2.visible = True
      self.col_calendar.visible = True
      self.render_calendar()

  def render_calendar(self):
    """Render simple month calendar"""
    self.col_calendar.clear()

    # Month/year header
    today = datetime.now()
    month_label = Label(
      text=today.strftime('%B %Y'),
      bold=True,
      font_size=16,
      align="center"
    )
    self.col_calendar.add_component(month_label)

    # Days of week
    dow_panel = FlowPanel()
    for day in ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']:
      dow_label = Label(
        text=day,
        bold=True,
        width=40,
        align="center"
      )
      dow_panel.add_component(dow_label)
    self.col_calendar.add_component(dow_panel)

    # Calendar grid (simplified - next 14 days)
    dates_panel = FlowPanel()
    for i in range(14):
      date = today + timedelta(days=i)
      date_btn = Button(
        text=str(date.day),
        width=40,
        height=40,
        role="outlined-button"
      )
      date_btn.tag = date.date()
      date_btn.set_event_handler('click', self.date_selected)
      dates_panel.add_component(date_btn)

    self.col_calendar.add_component(dates_panel)

  def date_selected(self, sender, **event_args):
    """Load time slots when date selected"""
    self.selected_date = sender.tag

    # Highlight selected button
    for btn in sender.parent.get_components():
      if hasattr(btn, 'tag') and btn.tag == self.selected_date:
        btn.role = "primary-color"
      else:
        btn.role = "outlined-button"

    # Load available time slots
    self.load_time_slots()

  def load_time_slots(self):
    """Load available time slots for selected date"""
    try:
      slots = anvil.server.call(
        'get_available_time_slots',
        self.selected_resource,
        self.selected_date
      )

      if slots:
        self.rp_timeslots.items = slots
        self.rp_timeslots.visible = True
      else:
        self.rp_timeslots.visible = False
        Notification("No available slots for this date", style="warning").show()

    except Exception as e:
      alert(f"Error loading time slots: {str(e)}")

  def time_slot_selected(self, time_slot):
    """Called by TimeSlotTemplate when time selected"""
    self.selected_time = time_slot

    # Show customer details form
    self.lbl_step3.visible = True
    self.txt_name.visible = True
    self.txt_email.visible = True
    self.txt_phone.visible = True
    self.txt_notes.visible = True
    self.btn_book_now.enabled = True

  def button_book_now_click(self, **event_args):
    """Submit booking"""
    try:
      self.lbl_message.visible = False

      # Validate
      if not self.txt_name.text:
        self.show_message("Name is required", "warning")
        return

      if not self.txt_email.text:
        self.show_message("Email is required", "warning")
        return

      if not self.selected_date or not self.selected_time:
        self.show_message("Please select date and time", "warning")
        return

      # Parse datetime
      hour, minute = map(int, self.selected_time.split(':'))
      booking_datetime = datetime.combine(
        self.selected_date,
        datetime.min.time()
      ).replace(hour=hour, minute=minute)

      # Submit booking
      result = anvil.server.call(
        'create_public_booking',
        {
          'resource_id': self.selected_resource,
          'start_datetime': booking_datetime,
          'customer_name': self.txt_name.text,
          'customer_email': self.txt_email.text,
          'customer_phone': self.txt_phone.text,
          'notes': self.txt_notes.text
        }
      )

      if result['success']:
        self.show_message(
          f"✅ Booking confirmed! Confirmation sent to {self.txt_email.text}",
          "success"
        )
        # Clear form
        self.reset_form()
      else:
        self.show_message(result['error'], "danger")

    except Exception as e:
      self.show_message(f"Error creating booking: {str(e)}", "danger")

  def reset_form(self):
    """Reset form to initial state"""
    self.dd_service.selected_value = None
    self.txt_name.text = ""
    self.txt_email.text = ""
    self.txt_phone.text = ""
    self.txt_notes.text = ""
    self.lbl_step2.visible = False
    self.col_calendar.visible = False
    self.rp_timeslots.visible = False
    self.lbl_step3.visible = False
    self.txt_name.visible = False
    self.txt_email.visible = False
    self.txt_phone.visible = False
    self.txt_notes.visible = False
    self.btn_book_now.enabled = False

  def show_message(self, text, style):
    """Display message"""
    self.lbl_message.text = text
    self.lbl_message.role = f"alert-{style}"
    self.lbl_message.visible = True

  @handle("dd_service", "change")
  def dd_service_change(self, **event_args):
    """This method is called when an item is selected"""
    pass

  @handle("btn_book_now", "click")
  def btn_book_now_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
