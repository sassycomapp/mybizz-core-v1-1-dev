from ._anvil_designer import BookingListFormTemplate
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

class BookingListForm(BookingListFormTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "Bookings"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True
    self.lbl_title.role = "headline"

    # Configure new booking button
    self.btn_new_booking.text = "New Booking"
    self.btn_new_booking.icon = "fa:plus"
    self.btn_new_booking.role = "primary-color"

    # Configure filters label
    self.lbl_filters.text = "Filters:"
    self.lbl_filters.bold = True

    # Configure status filter
    self.dd_status_filter.items = [
      ('All Statuses', 'all'),
      ('Pending', 'pending'),
      ('Confirmed', 'confirmed'),
      ('Completed', 'completed'),
      ('Cancelled', 'cancelled'),
      ('No Show', 'no_show')
    ]
    self.dd_status_filter.selected_value = 'all'
    self.dd_status_filter.placeholder = "Status"

    # Configure resource filter
    self.dd_resource_filter.placeholder = "All Resources"
    self.load_resources()

    # Configure date pickers
    self.dp_date_from.date = datetime.now().date() - timedelta(days=30)
    self.dp_date_to.date = datetime.now().date() + timedelta(days=30)

    # Configure search button
    self.btn_search.text = ""
    self.btn_search.icon = "fa:search"
    self.btn_search.role = "secondary-color"

    # Configure data grid
    self.dg_bookings.columns = [
      {'id': 'booking_number', 'title': 'Booking #', 'data_key': 'booking_number', 'width': 120},
      {'id': 'customer', 'title': 'Customer', 'data_key': 'customer_name', 'width': 150},
      {'id': 'resource', 'title': 'Resource', 'data_key': 'resource_name', 'width': 150},
      {'id': 'datetime', 'title': 'Date/Time', 'data_key': 'datetime_display', 'width': 180},
      {'id': 'status', 'title': 'Status', 'data_key': 'status', 'width': 100},
      {'id': 'actions', 'title': 'Actions', 'data_key': None, 'width': 100}
    ]

    # Configure no bookings label
    self.lbl_no_bookings.text = "No bookings found. Click 'New Booking' to create one!"
    self.lbl_no_bookings.align = "center"
    self.lbl_no_bookings.foreground = "#666666"
    self.lbl_no_bookings.visible = False

    # Load bookings
    self.load_bookings()

  def load_resources(self):
    """Load resources for filter"""
    try:
      resources = anvil.server.call('get_all_bookable_resources')
      self.dd_resource_filter.items = [('All Resources', None)] + [
        (r['resource_name'], r.get_id()) for r in resources
      ]
      self.dd_resource_filter.selected_value = None
    except Exception as e:
      print(f"Error loading resources: {e}")

  def load_bookings(self, **event_args):
    """Load bookings with filters"""
    try:
      filters = {
        'status': self.dd_status_filter.selected_value if self.dd_status_filter.selected_value != 'all' else None,
        'resource_id': self.dd_resource_filter.selected_value,
        'date_from': self.dp_date_from.date,
        'date_to': self.dp_date_to.date
      }

      bookings = anvil.server.call('get_all_bookings', filters)

      if bookings:
        # Add display fields
        for booking in bookings:
          # Customer name
          if booking.get('customer_id'):
            booking['customer_name'] = booking['customer_id']['email'].split('@')[0]
          else:
            booking['customer_name'] = 'Guest'

          # Resource name
          if booking.get('resource_id'):
            booking['resource_name'] = booking['resource_id']['resource_name']
          else:
            booking['resource_name'] = 'Unknown'

          # Date/time display
          start = booking['start_datetime']
          booking['datetime_display'] = f"{start.strftime('%b %d, %I:%M %p')}"

        self.dg_bookings.items = bookings
        self.dg_bookings.visible = True
        self.lbl_no_bookings.visible = False
      else:
        self.dg_bookings.visible = False
        self.lbl_no_bookings.visible = True

    except Exception as e:
      alert(f"Error loading bookings: {str(e)}")

  def button_new_booking_click(self, **event_args):
    """Create new booking"""
    open_form('bookings.BookingCreateForm')

  def dropdown_status_filter_change(self, **event_args):
    """Reload when filter changes"""
    self.load_bookings()

  def dropdown_resource_filter_change(self, **event_args):
    """Reload when filter changes"""
    self.load_bookings()

  def button_search_click(self, **event_args):
    """Search with date range"""
    self.load_bookings()

  def dg_bookings_row_click(self, row, **event_args):
    """Handle row click (handled by row template)"""
    pass

  @handle("btn_new_booking", "click")
  def btn_new_booking_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("dd_status_filter", "change")
  def dd_status_filter_change(self, **event_args):
    """This method is called when an item is selected"""
    pass

  @handle("dd_resource_filter", "change")
  def dd_resource_filter_change(self, **event_args):
    """This method is called when an item is selected"""
    pass

  @handle("btn_search", "click")
  def btn_search_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
