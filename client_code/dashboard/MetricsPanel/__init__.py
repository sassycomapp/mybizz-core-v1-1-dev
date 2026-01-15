from ._anvil_designer import MetricsPanelTemplate
from anvil import *
from routing import router
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class MetricsPanel(MetricsPanelTemplate):
  """Dashboard metrics widget showing key business indicators"""

  def __init__(self, **properties):
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "Key Metrics"
    self.lbl_title.font_size = 18
    self.lbl_title.bold = True

    # Configure refresh button
    self.btn_refresh.text = ""
    self.btn_refresh.icon = "fa:refresh"
    self.btn_refresh.role = "outlined-button"

    # Load metrics
    self.load_metrics()

  def load_metrics(self):
    """Load and display metrics"""
    try:
      # Show loading state
      self.fp_metrics.clear()
      self.add_loading_indicator()

      # Get metrics from server
      result = anvil.server.call('get_dashboard_metrics')

      if result['success']:
        data = result['data']

        # Clear loading
        self.fp_metrics.clear()

        # Create metric cards
        self.create_metric_card(
          "Today's Revenue",
          f"${data['today_revenue']:,.2f}",
          data.get('revenue_change', '+0%'),
          "green" if '+' in str(data.get('revenue_change', '')) else "red"
        )

        self.create_metric_card(
          "This Week's Bookings",
          str(data['week_bookings']),
          data.get('bookings_change', '+0'),
          "green" if '+' in str(data.get('bookings_change', '')) else "red"
        )

        self.create_metric_card(
          "New Customers",
          str(data['new_customers']),
          data.get('customers_change', '+0'),
          "green" if '+' in str(data.get('customers_change', '')) else "red"
        )

        self.create_metric_card(
          "Pending Tasks",
          str(data['pending_tasks']),
          data.get('tasks_change', '0'),
          "#666666"
        )

      else:
        self.fp_metrics.clear()
        error_label = Label(
          text=f"Error: {result.get('error', 'Unknown error')}",
          foreground="red"
        )
        self.fp_metrics.add_component(error_label)

    except Exception as e:
      print(f"Error loading metrics: {e}")
      self.fp_metrics.clear()
      error_label = Label(
        text="Failed to load metrics",
        foreground="red"
      )
      self.fp_metrics.add_component(error_label)

  def create_metric_card(self, title, value, change, change_color):
    """Create a metric card widget"""
    card = ColumnPanel(
      background='#F5F5F5',
      border='1px solid #E0E0E0',
      border_radius=8,
      spacing_above='small',
      spacing_below='small',
      width=200
    )

    # Title
    title_label = Label(
      text=title,
      font_size=12,
      foreground="#666666",
      bold=True,
      spacing_above='small',
      spacing_below='small'
    )
    card.add_component(title_label)

    # Value
    value_label = Label(
      text=value,
      font_size=32,
      bold=True,
      spacing_above='small',
      spacing_below='small'
    )
    card.add_component(value_label)

    # Change indicator
    if change and change != '0' and change != '+0%' and change != '+0':
      change_label = Label(
        text=change,
        font_size=14,
        foreground=change_color,
        spacing_above='small',
        spacing_below='small'
      )
      card.add_component(change_label)

    self.fp_metrics.add_component(card)

  def add_loading_indicator(self):
    """Show loading state"""
    loading = Label(
      text="Loading metrics...",
      foreground="#666666",
      italic=True
    )
    self.fp_metrics.add_component(loading)

  def button_refresh_click(self, **event_args):
    """Refresh metrics"""
    self.load_metrics()

  @handle("btn_refresh", "click")
  def btn_refresh_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
