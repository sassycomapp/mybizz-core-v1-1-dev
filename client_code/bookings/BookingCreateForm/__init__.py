from ._anvil_designer import BookingCreateFormTemplate
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

class BookingCreateForm(BookingCreateFormTemplate):
  def __init__(self, booking_id=None, start_datetime=None, resource_id=None, **properties):
    self.booking_id = booking_id
    self.metadata_schema = None
    self.metadata_values = {}
    self.init_components(**properties)

    # Configure title
    if self.booking_id:
      self.lbl_title.text = "Edit Booking"
    else:
      self.lbl_title.text = "Create New Booking"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True

    # Configure check availability button
    self.btn_check_availability.text = "Check Availability"
    self.btn_check_availability.icon = "fa:check-circle"
    self.btn_check_availability.role = "secondary-color"

    # Configure field labels
    self.lbl_customer_field.text = "Customer *"
    self.lbl_customer_field.bold = True

    self.lbl_resource_field.text = "Resource *"
    self.lbl_resource_field.bold = True

    self.lbl_type_field.text = "Booking Type *"
    self.lbl_type_field.bold = True

    self.lbl_start_field.text = "Start Date & Time *"
    self.lbl_start_field.bold = True

    self.lbl_end_field.text = "End Date & Time *"
    self.lbl_end_field.bold = True

    # Configure customer dropdown
    self.dd_customer.placeholder = "Search or select customer..."
    self.load_customers()

    # Configure resource dropdown
    self.dd_resource.placeholder = "Select room/staff/equipment..."
    self.load_resources()

    # Configure booking type dropdown
    self.dd_booking_type.items = [
      ('Room Booking', 'room'),
      ('Appointment', 'appointment'),
      ('Service Booking', 'service'),
      ('Event', 'event')
    ]
    self.dd_booking_type.placeholder = "Select booking type..."

    # Configure date/time pickers
    self.txt_start_time.placeholder = "HH:MM (24hr)"
    self.txt_end_time.placeholder = "HH:MM (24hr)"

    # Pre-fill if provided
    if start_datetime:
      self.dp_start_date.date = start_datetime.date()
      self.txt_start_time.text = start_datetime.strftime('%H:%M')
      # Default 1 hour duration
      end_dt = start_datetime + timedelta(hours=1)
      self.dp_end_date.date = end_dt.date()
      self.txt_end_time.text = end_dt.strftime('%H:%M')

    if resource_id:
      self.dd_resource.selected_value = resource_id

    # Configure total amount
    self.lbl_total_amount.text = "Total Amount: $0.00"
    self.lbl_total_amount.font_size = 18
    self.lbl_total_amount.bold = True

    # Configure availability indicator
    self.lbl_availability.visible = False

    # Configure message label
    self.lbl_message.visible = False
    self.lbl_message.align = "center"

    # Configure buttons
    self.btn_cancel.text = "Cancel"
    self.btn_cancel.role = "secondary-color"

    self.btn_save_pending.text = "Save as Pending"
    self.btn_save_pending.icon = "fa:save"
    self.btn_save_pending.role = "secondary-color"

    self.btn_confirm_pay.text = "Confirm & Pay"
    self.btn_confirm_pay.icon = "fa:credit-card"
    self.btn_confirm_pay.role = "primary-color"

    # Load existing booking if editing
    if self.booking_id:
      self.load_booking()

  def load_customers(self):
    """Load customer list"""
    try:
      customers = anvil.server.call('get_all_customers')
      self.dd_customer.items = [
        (f"{c['email']}", c.get_id()) for c in customers
      ]
    except Exception as e:
      print(f"Error loading customers: {e}")

  def load_resources(self):
    """Load bookable resources"""
    try:
      resources = anvil.server.call('get_all_bookable_resources')
      self.dd_resource.items = [
        (r['resource_name'], r.get_id()) for r in resources
      ]
    except Exception as e:
      print(f"Error loading resources: {e}")

  def load_booking(self):
    """Load existing booking for editing"""
    try:
      booking = anvil.server.call('get_booking', self.booking_id)
      if booking:
        self.dd_customer.selected_value = booking['customer_id'].get_id()
        self.dd_resource.selected_value = booking['resource_id'].get_id()
        self.dd_booking_type.selected_value = booking['booking_type']
        self.dp_start_date.date = booking['start_datetime'].date()
        self.txt_start_time.text = booking['start_datetime'].strftime('%H:%M')
        self.dp_end_date.date = booking['end_datetime'].date()
        self.txt_end_time.text = booking['end_datetime'].strftime('%H:%M')
        self.metadata_values = booking.get('metadata', {})
        self.lbl_total_amount.text = f"Total Amount: ${booking['total_amount']:.2f}"
    except Exception as e:
      alert(f"Error loading booking: {str(e)}")

  def dropdown_booking_type_change(self, **event_args):
    """Load metadata schema when booking type changes"""
    booking_type = self.dd_booking_type.selected_value
    if booking_type:
      self.load_metadata_schema(booking_type)

  def load_metadata_schema(self, booking_type):
    """Load and render metadata fields for booking type"""
    try:
      # Get schema from server
      self.metadata_schema = anvil.server.call(
        'get_booking_metadata_schema',
        booking_type
      )

      # Clear previous fields
      self.col_metadata.clear()

      # Add title
      title = Label(
        text=f"{booking_type.title()} Details",
        bold=True,
        font_size=16,
        spacing_above='medium'
      )
      self.col_metadata.add_component(title)

      # Render each field
      if self.metadata_schema:
        for field_def in self.metadata_schema.get('required_fields', []):
          self.render_metadata_field(field_def)

    except Exception as e:
      print(f"Error loading schema: {e}")

  def render_metadata_field(self, field_def):
    """Render a single metadata field"""
    field_name = field_def['field']
    field_type = field_def['type']
    required = field_def.get('required', False)

    # Label
    label_text = field_name.replace('_', ' ').title()
    if required:
      label_text += " *"

    label = Label(text=label_text, bold=True, spacing_above='small')
    self.col_metadata.add_component(label)

    # Input based on type
    if field_type == 'string':
      input_field = TextBox(
        placeholder=f"Enter {label_text.lower()}",
        text=self.metadata_values.get(field_name, '')
      )
    elif field_type == 'number':
      input_field = TextBox(
        type='number',
        placeholder=f"Enter {label_text.lower()}",
        text=str(self.metadata_values.get(field_name, ''))
      )
    elif field_type == 'date':
      input_field = DatePicker(
        date=self.metadata_values.get(field_name)
      )
    elif field_type == 'boolean':
      input_field = CheckBox(
        text=label_text,
        checked=self.metadata_values.get(field_name, False)
      )
    else:
      input_field = TextBox(
        placeholder=f"Enter {label_text.lower()}"
      )

    # Store reference
    input_field.tag = field_name  # Use tag to identify field later
    self.col_metadata.add_component(input_field)

  def collect_metadata(self):
    """Collect values from metadata fields"""
    metadata = {}
    for component in self.col_metadata.get_components():
      if hasattr(component, 'tag') and component.tag:
        field_name = component.tag
        if isinstance(component, TextBox):
          metadata[field_name] = component.text
        elif isinstance(component, DatePicker):
          metadata[field_name] = component.date
        elif isinstance(component, CheckBox):
          metadata[field_name] = component.checked
    return metadata

  def button_check_availability_click(self, **event_args):
    """Check if time slot is available"""
    try:
      # Validate inputs
      if not self.dd_resource.selected_value:
        self.show_message("Please select a resource", "warning")
        return

      if not self.dp_start_date.date or not self.txt_start_time.text:
        self.show_message("Please enter start date and time", "warning")
        return

      if not self.dp_end_date.date or not self.txt_end_time.text:
        self.show_message("Please enter end date and time", "warning")
        return

      # Parse datetimes
      start_dt = self.parse_datetime(self.dp_start_date.date, self.txt_start_time.text)
      end_dt = self.parse_datetime(self.dp_end_date.date, self.txt_end_time.text)

      # Check availability
      result = anvil.server.call(
        'check_availability',
        self.dd_resource.selected_value,
        start_dt,
        end_dt,
        self.booking_id  # Exclude current booking if editing
      )

      if result['available']:
        self.lbl_availability.text = "✅ Time slot is available!"
        self.lbl_availability.foreground = "green"
        self.lbl_availability.visible = True
      else:
        self.lbl_availability.text = f"⚠️ Not available: {result['reason']}"
        self.lbl_availability.foreground = "red"
        self.lbl_availability.visible = True

    except Exception as e:
      self.show_message(f"Error checking availability: {str(e)}", "danger")

  def parse_datetime(self, date, time_str):
    """Parse date and time string into datetime"""
    hour, minute = map(int, time_str.split(':'))
    return datetime.combine(date, datetime.min.time()).replace(hour=hour, minute=minute)

  def button_save_pending_click(self, **event_args):
    """Save booking with pending status"""
    self.save_booking('pending')

  def button_confirm_pay_click(self, **event_args):
    """Confirm booking and process payment"""
    self.save_booking('confirmed')

  def save_booking(self, status):
    """Save booking to database"""
    try:
      # Validate
      if not self.dd_customer.selected_value:
        self.show_message("Customer is required", "warning")
        return
      
      if not self.dd_resource.selected_value:
        self.show_message("Resource is required", "warning")
        return
      
      if not self.dd_booking_type.selected_value:
        self.show_message("Booking type is required", "warning")
        return
      
      # Parse datetimes
      start_dt = self.parse_datetime(self.dp_start_date.date, self.txt_start_time.text)
      end_dt = self.parse_datetime(self.dp_end_date.date, self.txt_end_time.text)
      
      # Collect metadata
      metadata = self.collect_metadata()
      
      # Prepare booking data
      booking_data = {
        'customer_id': self.dd_customer.selected_value,
        'resource_id': self.dd_resource.selected_value,
        'booking_type': self.dd_booking_type.selected_value,
        'start_datetime': start_dt,
        'end_datetime': end_dt,
        'status': status,
        'metadata': metadata,
        'total_amount': 0  # Calculate based on resource rate * duration
      }
      
      # Save via server
      result = anvil.server.call(
        'save_booking',
        self.booking_id,
        booking_data
      )
      
      if result['success']:
        Notification(f"Booking {status}!", style="success").show()
        open_form('bookings.BookingListForm')
      else:
        self.show_message(result['error'], "danger")
      
    except Exception as e:
      self.show_message(f"Error saving booking: {str(e)}", "danger")
  
  def button_cancel_click(self, **event_args):
    """Cancel and return to list"""
    open_form('bookings.BookingListForm')
  
  def show_message(self, text, style):
    """Display message"""
    self.lbl_message.text = text
    self.lbl_message.role = f"alert-{style}"
    self.lbl_message.visible = True

  @handle("btn_check_availability", "click")
  def btn_check_availability_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_confirm_pay", "click")
  def btn_confirm_pay_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_save_pending", "click")
  def btn_save_pending_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_cancel", "click")
  def btn_cancel_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("dd_booking_type", "change")
  def dd_booking_type_change(self, **event_args):
    """This method is called when an item is selected"""
    pass
