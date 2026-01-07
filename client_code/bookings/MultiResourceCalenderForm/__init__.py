from ._anvil_designer import MultiResourceCalenderFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class MultiResourceCalenderForm(MultiResourceCalenderFormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.current_view = 'day'
    self.current_date = datetime.now()
    self.resources = []
    self.bookings = []
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "Multi-Resource Calendar"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True
    self.lbl_title.role = "headline"

    # Configure view buttons
    self.btn_view_day.text = "Day"
    self.btn_view_week.text = "Week"

    self.btn_view_day.role = "primary-color"  # Default
    self.btn_view_week.role = "secondary-color"

    # Configure navigation
    self.btn_prev.text = "←"
    self.btn_prev.icon = "fa:chevron-left"

    self.btn_next.text = "→"
    self.btn_next.icon = "fa:chevron-right"

    self.btn_today.text = "Today"
    self.btn_today.role = "secondary-color"

    # Configure legend
    self.lbl_legend.text = "Legend: 🟦 Confirmed  🟧 Pending  ⬜ Available"
    self.lbl_legend.font_size = 12
    self.lbl_legend.foreground = "#666666"

    # Configure loading
    self.lbl_loading.text = "Loading calendar..."
    self.lbl_loading.align = "center"
    self.lbl_loading.visible = False

    # Load calendar
    self.refresh_calendar()

  def refresh_calendar(self):
    """Reload calendar"""
    self.lbl_loading.visible = True
    self.col_timeline.clear()

    try:
      # Calculate date range
      if self.current_view == 'day':
        start_date = self.current_date.replace(hour=0, minute=0, second=0)
        end_date = start_date + timedelta(days=1)
        hours = range(8, 20)  # 8 AM to 8 PM
      else:  # week
        start_date = self.current_date - timedelta(days=self.current_date.weekday())
        end_date = start_date + timedelta(days=7)
        hours = range(8, 20)

      # Load resources
      self.resources = anvil.server.call('get_all_bookable_resources')

      # Load bookings
      self.bookings = anvil.server.call(
        'get_bookings_for_calendar',
        start_date,
        end_date,
        None  # All resources
      )

      # Render timeline
      if self.current_view == 'day':
        self.render_day_timeline()
      else:
        self.render_week_timeline()

      self.lbl_loading.visible = False

    except Exception as e:
      alert(f"Error loading calendar: {str(e)}")
      self.lbl_loading.visible = False

  def render_day_timeline(self):
    """Render day view with timeline"""
    # Date header
    date_label = Label(
      text=self.current_date.strftime('%A, %B %d, %Y'),
      bold=True,
      font_size=16,
      align="center"
    )
    self.col_timeline.add_component(date_label)

    # Create timeline grid
    # Header row (hours)
    header_row = FlowPanel()

    # Resource label column (empty top-left cell)
    header_row.add_component(Label(text="", width=100))

    # Hour columns
    for hour in range(8, 20):
      hour_label = Label(
        text=f"{hour:02d}:00",
        bold=True,
        width=80,
        align="center",
        foreground="#666666"
      )
      header_row.add_component(hour_label)

    self.col_timeline.add_component(header_row)

    # Resource rows
    for resource in self.resources:
      resource_row = FlowPanel(spacing_above='small')

      # Resource name
      name_label = Label(
        text=resource['resource_name'],
        bold=True,
        width=100
      )
      resource_row.add_component(name_label)

      # Hour cells for this resource
      for hour in range(8, 20):
        slot_time = self.current_date.replace(hour=hour, minute=0, second=0)

        # Check if booking exists in this slot
        booking_in_slot = None
        for booking in self.bookings:
          if (booking['resource_id'].get_id() == resource.get_id() and
              booking['start_datetime'].hour == hour and
              booking['start_datetime'].date() == self.current_date.date()):
            booking_in_slot = booking
            break

        if booking_in_slot:
          # Show booking
          cell = self.create_booking_cell(booking_in_slot)
        else:
          # Show available slot
          cell = self.create_available_cell(slot_time, resource)

        resource_row.add_component(cell)

      self.col_timeline.add_component(resource_row)

  def render_week_timeline(self):
    """Render week view timeline"""
    week_start = self.current_date - timedelta(days=self.current_date.weekday())

    # Week header
    week_label = Label(
      text=f"Week of {week_start.strftime('%B %d, %Y')}",
      bold=True,
      font_size=16,
      align="center"
    )
    self.col_timeline.add_component(week_label)

    # Day headers
    day_row = FlowPanel()
    day_row.add_component(Label(text="", width=100))  # Resource column

    for i in range(7):
      day = week_start + timedelta(days=i)
      day_label = Label(
        text=day.strftime('%a %d'),
        bold=True,
        width=100,
        align="center"
      )
      day_row.add_component(day_label)

    self.col_timeline.add_component(day_row)

    # Resource rows
    for resource in self.resources:
      resource_row = FlowPanel(spacing_above='small')

      # Resource name
      name_label = Label(
        text=resource['resource_name'],
        bold=True,
        width=100
      )
      resource_row.add_component(name_label)

      # Day cells
      for i in range(7):
        day = week_start + timedelta(days=i)

        # Count bookings for this resource on this day
        booking_count = len([
          b for b in self.bookings
          if b['resource_id'].get_id() == resource.get_id() and
          b['start_datetime'].date() == day.date()
        ])

        # Show count
        if booking_count > 0:
          cell = Button(
            text=f"{booking_count}",
            width=100,
            height=50,
            background="#2196F3",
            foreground="white",
            bold=True
          )
        else:
          cell = Button(
            text="Available",
            width=100,
            height=50,
            role="outlined-button"
          )

        # Click to view day
        cell.tag = {'date': day, 'resource': resource}
        cell.set_event_handler('click', self.day_cell_clicked)

        resource_row.add_component(cell)

      self.col_timeline.add_component(resource_row)

  def create_booking_cell(self, booking):
    """Create cell for booked slot"""
    customer_name = "Guest"
    if booking.get('customer_id'):
      customer_name = booking['customer_id']['email'].split('@')[0]

    color = self.get_status_color(booking['status'])

    cell = Button(
      text=customer_name[:8],
      width=80,
      height=50,
      background=color,
      foreground="white",
      bold=True
    )

    cell.tag = booking
    cell.set_event_handler('click', self.booking_clicked)

    return cell

  def create_available_cell(self, slot_time, resource):
    """Create cell for available slot"""
    cell = Button(
      text="",
      width=80,
      height=50,
      background="#f0f0f0",
      role="outlined-button"
    )

    cell.tag = {'time': slot_time, 'resource': resource}
    cell.set_event_handler('click', self.available_slot_clicked)

    return cell

  def get_status_color(self, status):
    """Get color for status"""
    colors = {
      'confirmed': '#2196F3',
      'pending': '#FF9800',
      'completed': '#4CAF50',
      'cancelled': '#F44336'
    }
    return colors.get(status, '#CCCCCC')

  def booking_clicked(self, sender, **event_args):
    """Handle booking click"""
    booking = sender.tag
    alert(f"Booking: {booking['booking_number']}\nCustomer: {booking.get('customer_id', {}).get('email', 'Guest')}\nStatus: {booking['status']}")
    # TODO: Open BookingDetailForm

  def available_slot_clicked(self, sender, **event_args):
    """Handle available slot click"""
    slot_data = sender.tag
    open_form('bookings.BookingCreateForm',
              start_datetime=slot_data['time'],
              resource_id=slot_data['resource'].get_id())

  def day_cell_clicked(self, sender, **event_args):
    """Switch to day view for clicked day"""
    cell_data = sender.tag
    self.current_date = cell_data['date']
    self.current_view = 'day'
    self.btn_view_day.role = "primary-color"
    self.btn_view_week.role = "secondary-color"
    self.refresh_calendar()

  def button_view_day_click(self, **event_args):
    """Switch to day view"""
    self.current_view = 'day'
    self.btn_view_day.role = "primary-color"
    self.btn_view_week.role = "secondary-color"
    self.refresh_calendar()

  def button_view_week_click(self, **event_args):
    """Switch to week view"""
    self.current_view = 'week'
    self.btn_view_week.role = "primary-color"
    self.btn_view_day.role = "secondary-color"
    self.refresh_calendar()

  def button_prev_click(self, **event_args):
    """Navigate to previous period"""
    if self.current_view == 'day':
      self.current_date -= timedelta(days=1)
    else:
      self.current_date -= timedelta(days=7)
    self.refresh_calendar()

  def button_next_click(self, **event_args):
    """Navigate to next period"""
    if self.current_view == 'day':
      self.current_date += timedelta(days=1)
    else:
      self.current_date += timedelta(days=7)
    self.refresh_calendar()

  def button_today_click(self, **event_args):
    """Jump to today"""
    self.current_date = datetime.now()
    self.refresh_calendar()

  @handle("btn_today", "click")
  """Jump to today"""
  self.current_date = datetime.now()
  self.refresh_calendar()

  @handle("btn_view_day", "click")
  def btn_view_day_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_view_week", "click")
  def btn_view_week_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_prev", "click")
  def btn_prev_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_next", "click")
  def btn_next_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_today", "click")
  def btn_today_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
