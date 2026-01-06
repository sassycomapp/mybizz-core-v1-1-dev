from ._anvil_designer import BookingAnalyticsWidgetTemplate
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

class BookingAnalyticsWidget(BookingAnalyticsWidgetTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "Booking Analytics"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True
    self.lbl_title.role = "headline"

    # Configure date range dropdown
    self.dd_date_range.items = [
      ('Last 7 Days', 7),
      ('Last 30 Days', 30),
      ('Last 90 Days', 90)
    ]
    self.dd_date_range.selected_value = 30

    # Configure sections
    self.lbl_top_resources_section.text = "MOST BOOKED RESOURCES"
    self.lbl_top_resources_section.bold = True
    self.lbl_top_resources_section.font_size = 16

    self.lbl_peak_times_section.text = "PEAK BOOKING TIMES"
    self.lbl_peak_times_section.bold = True
    self.lbl_peak_times_section.font_size = 16

    # Set repeating panel template
    self.rp_top_resources.item_template = 'bookings.TopResourceTemplate'

    # Load analytics
    self.load_analytics()

  def load_analytics(self):
    """Load analytics data"""
    try:
      days = self.dd_date_range.selected_value

      # Get analytics from server
      analytics = anvil.server.call('get_booking_analytics', days)

      # Display stats cards
      self.display_stats_cards(analytics)

      # Display top resources
      if analytics.get('top_resources'):
        self.rp_top_resources.items = analytics['top_resources']

      # Display peak times
      if analytics.get('peak_times'):
        self.display_peak_times(analytics['peak_times'])

    except Exception as e:
      alert(f"Error loading analytics: {str(e)}")

  def display_stats_cards(self, analytics):
    """Display stats cards"""
    self.fp_stats_cards.clear()

    # Booking count card
    bookings_card = self.create_stat_card(
      "Bookings",
      str(analytics.get('total_bookings', 0)),
      analytics.get('bookings_change', '+0%')
    )
    self.fp_stats_cards.add_component(bookings_card)

    # Revenue card
    revenue_card = self.create_stat_card(
      "Revenue",
      f"${analytics.get('total_revenue', 0):,.0f}",
      analytics.get('revenue_change', '+0%')
    )
    self.fp_stats_cards.add_component(revenue_card)

    # No-shows card
    noshows_card = self.create_stat_card(
      "No-Shows",
      str(analytics.get('no_shows', 0)),
      analytics.get('noshows_change', '0%')
    )
    self.fp_stats_cards.add_component(noshows_card)

    # Avg value card
    avg_card = self.create_stat_card(
      "Avg Value",
      f"${analytics.get('avg_booking_value', 0):.0f}",
      analytics.get('avg_change', '+0%')
    )
    self.fp_stats_cards.add_component(avg_card)

  def create_stat_card(self, title, value, change):
    """Create a stat card"""
    card = ColumnPanel(
      background='#F5F5F5',
      spacing_above='small',
      spacing_below='small',
      width=150
    )

    # Title
    title_label = Label(
      text=title,
      bold=True,
      font_size=12,
      foreground="#666666"
    )
    card.add_component(title_label)

    # Value
    value_label = Label(
      text=value,
      bold=True,
      font_size=24
    )
    card.add_component(value_label)

    # Change
    change_color = "green" if "↑" in change or "+" in change else "red"
    change_label = Label(
      text=change,
      font_size=12,
      foreground=change_color
    )
    card.add_component(change_label)

    return card

  def display_peak_times(self, peak_times):
    """Display peak times chart"""
    self.col_peak_times.clear()

    if not peak_times:
      no_data = Label(
        text="No data available",
        foreground="#666666",
        italic=True
      )
      self.col_peak_times.add_component(no_data)
      return

    # Find max count for scaling
    max_count = max(item['count'] for item in peak_times)

    # Create bars
    for item in peak_times:
      row = FlowPanel(spacing_above='small')

      # Time label
      time_label = Label(
        text=item['time'],
        width=50,
        bold=True
      )
      row.add_component(time_label)

      # Bar
      bar_width = int((item['count'] / max_count) * 300) if max_count > 0 else 0
      bar = Label(
        text="■" * int(bar_width / 10),
        foreground="#2196F3",
        width=bar_width
      )
      row.add_component(bar)

      # Count label
      count_label = Label(
        text=f" {item['count']} bookings",
        foreground="#666666"
      )
      row.add_component(count_label)

      self.col_peak_times.add_component(row)

  def dropdown_date_range_change(self, **event_args):
    """Reload analytics when date range changes"""
    self.load_analytics()

  @handle("dd_date_range", "change")
  def dd_date_range_change(self, **event_args):
    """This method is called when an item is selected"""
    pass
