from ._anvil_designer import CheckInOutFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime

class CheckInOutForm(CheckInOutFormTemplate):
  def __init__(self, booking_id=None, **properties):
    self.current_booking = None
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "Check-In / Check-Out"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True
    self.lbl_title.role = "headline"

    # Configure search
    self.txt_search.placeholder = "Enter booking number or guest name"
    self.txt_search.icon = "fa:search"

    self.btn_search.text = ""
    self.btn_search.icon = "fa:search"
    self.btn_search.role = "primary-color"

    # Configure check-in section
    self.lbl_checkin_section.text = "CHECK-IN"
    self.lbl_checkin_section.bold = True
    self.lbl_checkin_section.font_size = 16

    self.lbl_id_field.text = "ID Document (Passport/License)"
    self.lbl_id_field.bold = True

    self.txt_id_document.placeholder = "Document number"

    self.lbl_key_field.text = "Room Key Number"
    self.lbl_key_field.bold = True

    self.txt_key_number.placeholder = "Key #"

    self.lbl_requests_field.text = "Special Requests / Notes"
    self.lbl_requests_field.bold = True

    self.txt_requests.placeholder = "Any special requests..."
    self.txt_requests.rows = 3

    self.btn_check_in.text = "Process Check-In"
    self.btn_check_in.icon = "fa:sign-in"
    self.btn_check_in.role = "primary-color"
    self.btn_check_in.enabled = False

    # Configure check-out section
    self.lbl_checkout_section.text = "CHECK-OUT"
    self.lbl_checkout_section.bold = True
    self.lbl_checkout_section.font_size = 16

    self.lbl_room_charges.text = "Room Charges: $0.00"
    self.lbl_room_charges.font_size = 14

    self.lbl_extras_field.text = "Additional Charges / Extras"
    self.lbl_extras_field.bold = True

    self.txt_extras.type = "number"
    self.txt_extras.placeholder = "0.00"
    self.txt_extras.text = "0"

    self.lbl_tax.text = "Tax: $0.00"
    self.lbl_tax.font_size = 14

    self.lbl_total.text = "TOTAL: $0.00"
    self.lbl_total.font_size = 18
    self.lbl_total.bold = True

    self.lbl_payment_field.text = "Payment Status"
    self.lbl_payment_field.bold = True

    self.dd_payment_status.items = [
      ('Paid', 'paid'),
      ('Pending', 'pending'),
      ('Partial', 'partial')
    ]
    self.dd_payment_status.selected_value = 'paid'

    self.btn_check_out.text = "Process Check-Out"
    self.btn_check_out.icon = "fa:sign-out"
    self.btn_check_out.role = "primary-color"
    self.btn_check_out.enabled = False

    # Initially hide details and action sections
    self.col_booking_details.visible = False
    self.lbl_checkin_section.visible = False
    self.txt_id_document.visible = False
    self.txt_key_number.visible = False
    self.txt_requests.visible = False
    self.btn_check_in.visible = False
    self.lbl_checkout_section.visible = False
    self.lbl_room_charges.visible = False
    self.txt_extras.visible = False
    self.lbl_tax.visible = False
    self.lbl_total.visible = False
    self.dd_payment_status.visible = False
    self.btn_check_out.visible = False

    # Load booking if provided
    if booking_id:
      self.load_booking(booking_id)

  def button_search_click(self, **event_args):
    """Search for booking"""
    search_term = self.txt_search.text
    if not search_term:
      alert("Please enter a booking number or guest name")
      return

    try:
      booking = anvil.server.call('search_booking_for_checkin', search_term)

      if booking:
        self.display_booking(booking)
      else:
        alert("Booking not found")

    except Exception as e:
      alert(f"Error searching: {str(e)}")

  def load_booking(self, booking_id):
    """Load specific booking"""
    try:
      booking = anvil.server.call('get_booking', booking_id)
      if booking:
        self.display_booking(booking)
    except Exception as e:
      alert(f"Error loading booking: {str(e)}")

  def display_booking(self, booking):
    """Display booking details and show appropriate actions"""
    self.current_booking = booking

    # Clear and show booking details
    self.col_booking_details.clear()
    self.col_booking_details.visible = True

    # Add details
    title = Label(text="BOOKING DETAILS", bold=True, font_size=16)
    self.col_booking_details.add_component(title)

    booking_num = Label(
      text=f"Booking #: {booking['booking_number']}",
      spacing_above='small'
    )
    self.col_booking_details.add_component(booking_num)

    guest_name = "Guest"
    if booking.get('customer_id'):
      guest_name = booking['customer_id']['email'].split('@')[0]

    guest = Label(text=f"Guest: {guest_name}")
    self.col_booking_details.add_component(guest)

    room_info = "Unknown Room"
    if booking.get('resource_id'):
      room_info = f"{booking['resource_id']['room_number']} - {booking['resource_id']['room_type']}"

    room = Label(text=f"Room: {room_info}")
    self.col_booking_details.add_component(room)

    checkin_date = booking['start_datetime'].strftime('%b %d, %Y')
    checkout_date = booking['end_datetime'].strftime('%b %d, %Y')
    nights = (booking['end_datetime'].date() - booking['start_datetime'].date()).days

    dates = Label(text=f"Check-In: {checkin_date}")
    self.col_booking_details.add_component(dates)

    dates2 = Label(text=f"Check-Out: {checkout_date} ({nights} nights)")
    self.col_booking_details.add_component(dates2)

    status = Label(
      text=f"Status: {booking['status'].capitalize()}",
      bold=True,
      spacing_above='small'
    )
    self.col_booking_details.add_component(status)

    # Show appropriate action section based on status
    if booking['status'] == 'confirmed':
      # Can check in
      self.show_checkin_section()
    elif booking['status'] == 'checked_in':
      # Can check out
      self.show_checkout_section(booking)
    else:
      Notification(f"Booking status is '{booking['status']}' - no action available", style="info").show()

  def show_checkin_section(self):
    """Show check-in form"""
    self.lbl_checkin_section.visible = True
    self.lbl_id_field.visible = True
    self.txt_id_document.visible = True
    self.lbl_key_field.visible = True
    self.txt_key_number.visible = True
    self.lbl_requests_field.visible = True
    self.txt_requests.visible = True
    self.btn_check_in.visible = True
    self.btn_check_in.enabled = True

    # Hide checkout
    self.lbl_checkout_section.visible = False
    self.lbl_room_charges.visible = False
    self.lbl_extras_field.visible = False
    self.txt_extras.visible = False
    self.lbl_tax.visible = False
    self.lbl_total.visible = False
    self.lbl_payment_field.visible = False
    self.dd_payment_status.visible = False
    self.btn_check_out.visible = False

  def show_checkout_section(self, booking):
    """Show check-out form with charges"""
    # Calculate charges
    room_charges = booking.get('total_amount', 0)
    self.lbl_room_charges.text = f"Room Charges: ${room_charges:.2f}"

    # Hide checkin
    self.lbl_checkin_section.visible = False
    self.txt_id_document.visible = False
    self.txt_key_number.visible = False
    self.txt_requests.visible = False
    self.btn_check_in.visible = False

    # Show checkout
    self.lbl_checkout_section.visible = True
    self.lbl_room_charges.visible = True
    self.lbl_extras_field.visible = True
    self.txt_extras.visible = True
    self.lbl_tax.visible = True
    self.lbl_total.visible = True
    self.lbl_payment_field.visible = True
    self.dd_payment_status.visible = True
    self.btn_check_out.visible = True
    self.btn_check_out.enabled = True
    
    # Update total when extras change
    self.calculate_checkout_total()
  
  def textbox_extras_change(self, **event_args):
    """Recalculate total when extras change"""
    self.calculate_checkout_total()
  
  def calculate_checkout_total(self):
    """Calculate and display checkout total"""
    if not self.current_booking:
      return
    
    room_charges = self.current_booking.get('total_amount', 0)
    extras = float(self.txt_extras.text or 0)
    subtotal = room_charges + extras
    
    # Calculate tax (10%)
    tax = subtotal * 0.10
    total = subtotal + tax
    
    self.lbl_tax.text = f"Tax (10%): ${tax:.2f}"
    self.lbl_total.text = f"TOTAL: ${total:.2f}"
  
  def button_check_in_click(self, **event_args):
    """Process check-in"""
    try:
      if not self.txt_id_document.text:
        alert("ID Document is required")
        return
      
      checkin_data = {
        'id_document': self.txt_id_document.text,
        'key_number': self.txt_key_number.text,
        'special_requests': self.txt_requests.text
      }
      
      result = anvil.server.call(
        'process_check_in',
        self.current_booking.get_id(),
        checkin_data
      )
      
      if result['success']:
        Notification("✅ Check-in successful!", style="success").show()
        # Refresh booking
        self.load_booking(self.current_booking.get_id())
      else:
        alert(result['error'])
        
    except Exception as e:
      alert(f"Error processing check-in: {str(e)}")
  
  def button_check_out_click(self, **event_args):
    """Process check-out"""
    try:
      room_charges = self.current_booking.get('total_amount', 0)
      extras = float(self.txt_extras.text or 0)
      subtotal = room_charges + extras
      tax = subtotal * 0.10
      total = subtotal + tax
      
      checkout_data = {
        'extras': extras,
        'tax': tax,
        'total': total,
        'payment_status': self.dd_payment_status.selected_value
      }
      
      result = anvil.server.call(
        'process_check_out',
        self.current_booking.get_id(),
        checkout_data
      )
      
      if result['success']:
        Notification("✅ Check-out successful!", style="success").show()
        # Clear form
        self.reset_form()
      else:
        alert(result['error'])
        
    except Exception as e:
      alert(f"Error processing check-out: {str(e)}")
  
  def reset_form(self):
    """Reset form to initial state"""
    self.txt_search.text = ""
    self.txt_id_document.text = ""
    self.txt_key_number.text = ""
    self.txt_requests.text = ""
    self.txt_extras.text = "0"
    self.current_booking = None
    self.col_booking_details.visible = False
    self.lbl_checkin_section.visible = False
    self.txt_id_document.visible = False
    self.txt_key_number.visible = False
    self.txt_requests.visible = False
    self.btn_check_in.visible = False
    self.lbl_checkout_section.visible = False
    self.lbl_room_charges.visible = False
    self.txt_extras.visible = False
    self.lbl_tax.visible = False
    self.lbl_total.visible = False
    self.dd_payment_status.visible = False
    self.btn_check_out.visible = False

  @handle("btn_search", "click")
  def btn_search_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("txt_extras", "pressed_enter")
  def txt_extras_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    pass

  @handle("btn_check_in", "click")
  def btn_check_in_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_check_out", "click")
  def btn_check_out_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
