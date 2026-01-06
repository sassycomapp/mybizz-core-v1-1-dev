from ._anvil_designer import BookingCalendarComponentTemplate
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

class BookingCalendarComponent(BookingCalendarComponentTemplate):
  def __init__(self, **properties):
    self.current_view = 'week'  # day, week, month
    self.current_date = datetime.now()
    self.selected_resource = None
    self.bookings = []
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "📅 Booking Calendar"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True
    self.lbl_title.role = "headline"

    # Configure view buttons
    self.btn_view_day.text = "Day"
    self.btn_view_week.text = "Week"
    self.btn_view_month.text = "Month"

    self.btn_view_week.role = "primary-color"  # Default view
    self.btn_view_day.role = "secondary-color"
    self.btn_view_month.role = "secondary-color"

    # Configure navigation buttons
    self.btn_prev.text = "←"
    self.btn_prev.icon = "fa:chevron-left"

    self.btn_next.text = "→"
    self.btn_next.icon = "fa:chevron-right"

    self.btn_today.text = "Today"
    self.btn_today.role = "secondary-color"

    # Configure resource filter
    self.dd_resource_filter.placeholder = "Filter by resource"
    self.load_resources()

    # Configure legend
    self.lbl_legend.text = "🟦 Confirmed  🟧 Pending  🟥 Blocked  ⬜ Available"
    self.lbl_legend.font_size = 12
    self.lbl_legend.foreground = "#666666"

    # Configure loading indicator
    self.lbl_loading.text = "Loading calendar..."
    self.lbl_loading.align = "center"
    self.lbl_loading.visible = False

    # Load calendar
    self.refresh_calendar()

  def load_resources(self):
    """Load available resources for filter"""
    try:
      resources = anvil.server.call('get_all_bookable_resources')
      self.dd_resource_filter.items = [('All Resources', None)] + [
        (r['resource_name'], r.get_id()) for r in resources
      ]
      self.dd_resource_filter.selected_value = None
    except Exception as e:
      print(f"Error loading resources: {e}")

  def refresh_calendar(self):
    """Reload calendar with current view/date/filter"""
    self.lbl_loading.visible = True
    self.col_calendar.clear()

    try:
      # Calculate date range based on view
      if self.current_view == 'day':
        start_date = self.current_date.replace(hour=0, minute=0, second=0)
        end_date = start_date + timedelta(days=1)
      elif self.current_view == 'week':
        # Start of week (Monday)
        start_date = self.current_date - timedelta(days=self.current_date.weekday())
        end_date = start_date + timedelta(days=7)
      else:  # month
        start_date = self.current_date.replace(day=1, hour=0, minute=0, second=0)
        # End of month
        if start_date.month == 12:
          end_date = start_date.replace(year=start_date.year+1, month=1)
        else:
          end_date = start_date.replace(month=start_date.month+1)

      # Load bookings for date range
      self.bookings = anvil.server.call(
        'get_bookings_for_calendar',
        start_date,
        end_date,
        self.selected_resource
      )

      # Render appropriate view
      if self.current_view == 'day':
        self.render_day_view()
      elif self.current_view == 'week':
        self.render_week_view()
      else:
        self.render_month_view()

      self.lbl_loading.visible = False

    except Exception as e:
      alert(f"Error loading calendar: {str(e)}")
      self.lbl_loading.visible = False

  def render_day_view(self):
    """Render day view with hourly slots"""
    # Create day grid (24 hours x 1 day)
    day_label = Label(
      text=self.current_date.strftime('%A, %B %d, %Y'),
      bold=True,
      font_size=16
    )
    self.col_calendar.add_component(day_label)

    # Create hourly slots
    for hour in range(8, 20):  # 8 AM to 8 PM
      slot_time = self.current_date.replace(hour=hour, minute=0)

      # Check if any bookings in this hour
      bookings_in_slot = [
        b for b in self.bookings 
        if b['start_datetime'].hour == hour
      ]

      if bookings_in_slot:
        # Show booking
        for booking in bookings_in_slot:
          booking_card = self.create_booking_card(booking)
          self.col_calendar.add_component(booking_card)
      else:
        # Show available slot
        available_slot = self.create_available_slot(slot_time)
        self.col_calendar.add_component(available_slot)

  def render_week_view(self):
    """Render week view (7 days with time blocks)"""
    # This is complex - simplified version
    week_start = self.current_date - timedelta(days=self.current_date.weekday())

    # Create day headers
    day_row = FlowPanel()
    for i in range(7):
      day = week_start + timedelta(days=i)
      day_label = Label(
        text=day.strftime('%a %d'),
        bold=True,
        width=100
      )
      day_row.add_component(day_label)
    self.col_calendar.add_component(day_row)

    # Create time slots
    for hour in range(8, 20):
      hour_row = FlowPanel()

      # Time label
      time_label = Label(
        text=f"{hour:02d}:00",
        width=50,
        foreground="#666666"
      )
      hour_row.add_component(time_label)

      # Day cells
      for i in range(7):
        day = week_start + timedelta(days=i)
        slot_time = day.replace(hour=hour, minute=0)

        # Check bookings
        bookings_in_slot = [
          b for b in self.bookings
          if b['start_datetime'].date() == day.date() and
          b['start_datetime'].hour == hour
        ]

        if bookings_in_slot:
          cell = self.create_mini_booking_card(bookings_in_slot[0])
        else:
          cell = self.create_mini_available_slot(slot_time)

        hour_row.add_component(cell)

      self.col_calendar.add_component(hour_row)

  def render_month_view(self):
    """Render month view (grid of days)"""
    month_start = self.current_date.replace(day=1)
    month_label = Label(
      text=month_start.strftime('%B %Y'),
      bold=True,
      font_size=18
    )
    self.col_calendar.add_component(month_label)

    # Calendar grid (simplified - would need proper grid)
    info_label = Label(
      text="Month view: Shows availability at a glance",
      foreground="#666666",
      italic=True
    )
    self.col_calendar.add_component(info_label)

    # Show booking count per day
    for day_num in range(1, 32):
      try:
        day = month_start.replace(day=day_num)
        bookings_count = len([
          b for b in self.bookings
          if b['start_datetime'].date() == day.date()
        ])

        if bookings_count > 0:
          day_label = Label(
            text=f"Day {day_num}: {bookings_count} bookings"
          )
          self.col_calendar.add_component(day_label)
      except ValueError:
        break  # End of month

  def create_booking_card(self, booking):
    """Create booking display card"""
    card = ColumnPanel(
      background=self.get_status_color(booking['status']),
      spacing_above='small',
      spacing_below='small'
    )

    title = Label(
      text=f"{booking['customer_name']} - {booking['resource_name']}",
      bold=True
    )
    card.add_component(title)

    time_range = Label(
      text=f"{booking['start_datetime'].strftime('%I:%M %p')} - {booking['end_datetime'].strftime('%I:%M %p')}"
    )
    card.add_component(time_range)

    # Click to view details
    card.set_event_handler('click', lambda **e: self.view_booking_details(booking))

    return card

  def create_mini_booking_card(self, booking):
    """Create small booking card for week view"""
    return Button(
      text=booking['customer_name'][:10],
      background=self.get_status_color(booking['status']),
      width=100,
      height=40
    )

  def create_available_slot(self, slot_time):
    """Create clickable available slot"""
    slot = Button(
      text=f"Available at {slot_time.strftime('%I:%M %p')}",
      role="outlined-button",
      icon="fa:plus"
    )
    slot.set_event_handler('click', lambda **e: self.create_new_booking(slot_time))
    return slot

  def create_mini_available_slot(self, slot_time):
    """Create small available slot for week view"""
    slot = Button(
      text="",
      background="#f0f0f0",
      width=100,
      height=40
    )
    slot.set_event_handler('click', lambda **e: self.create_new_booking(slot_time))
    return slot

  def get_status_color(self, status):
    """Get color for booking status"""
    colors = {
      'confirmed': '#2196F3',  # Blue
      'pending': '#FF9800',    # Orange
      'completed': '#4CAF50',  # Green
      'cancelled': '#F44336',  # Red
      'no_show': '#9E9E9E'     # Gray
    }
    return colors.get(status, '#CCCCCC')

  def view_booking_details(self, booking):
    """Open booking details (placeholder)"""
    alert(f"Booking Details:\n\n{booking['booking_number']}\n{booking['customer_name']}\n{booking['resource_name']}")
    # TODO: Open BookingDetailForm

  def create_new_booking(self, slot_time):
    """Open booking creation form"""
    # Open BookingCreateForm with pre-filled time
    open_form('bookings.BookingCreateForm', 
              start_datetime=slot_time,
              resource_id=self.selected_resource)

  def button_view_day_click(self, **event_args):
    """Switch to day view"""
    self.current_view = 'day'
    self.btn_view_day.role = "primary-color"
    self.btn_view_week.role = "secondary-color"
    self.btn_view_month.role = "secondary-color"
    self.refresh_calendar()

  def button_view_week_click(self, **event_args):
    """Switch to week view"""
    self.current_view = 'week'
    self.btn_view_week.role = "primary-color"
    self.btn_view_day.role = "secondary-color"
    self.btn_view_month.role = "secondary-color"
    self.refresh_calendar()

  def button_view_month_click(self, **event_args):
    """Switch to month view"""
    self.current_view = 'month'
    self.btn_view_month.role = "primary-color"
    self.btn_view_day.role = "secondary-color"
    self.btn_view_week.role = "secondary-color"
    self.refresh_calendar()

  def button_prev_click(self, **event_args):
    """Navigate to previous period"""
    if self.current_view == 'day':
      self.current_date -= timedelta(days=1)
    elif self.current_view == 'week':
      self.current_date -= timedelta(days=7)
    else:  # month
      if self.current_date.month == 1:
        self.current_date = self.current_date.replace(year=self.current_date.year-1, month=12)
      else:
        self.current_date = self.current_date.replace(month=self.current_date.month-1)
    self.refresh_calendar()
  
  def button_next_click(self, **event_args):
    """Navigate to next period"""
    if self.current_view == 'day':
      self.current_date += timedelta(days=1)
    elif self.current_view == 'week':
      self.current_date += timedelta(days=7)
    else:  # month
      if self.current_date.month == 12:
        self.current_date = self.current_date.replace(year=self.current_date.year+1, month=1)
      else:
        self.current_date = self.current_date.replace(month=self.current_date.month+1)
    self.refresh_calendar()
  
  def button_today_click(self, **event_args):
    """Jump to today"""
    self.current_date = datetime.now()
    self.refresh_calendar()
  
  def dropdown_resource_filter_change(self, **event_args):
    """Filter calendar by resource"""
    self.selected_resource = self.dd_resource_filter.selected_value
    self.refresh_calendar()

  @handle("btn_view_day", "click")
  def btn_view_day_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_view_week", "click")
  def btn_view_week_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_view_month", "click")
  def btn_view_month_click(self, **event_args):
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

  @handle("dd_resource_filter", "change")
  def dd_resource_filter_change(self, **event_args):
    """This method is called when an item is selected"""
    pass
