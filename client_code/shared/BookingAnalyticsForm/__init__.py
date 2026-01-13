from ._anvil_designer import BookingAnalyticsFormTemplate
from anvil import *
import plotly.graph_objects as go
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class BookingAnalyticsForm(BookingAnalyticsFormTemplate):
  """Booking analytics dashboard"""

  def __init__(self, **properties):
    self.init_components(**properties)

    # Check permissions
    user = anvil.users.get_user()
    if not user or user['role'] not in ['owner', 'manager']:
      alert("Access denied")
      open_form('dashboard.DashboardForm')
      return

    # Configure title
    self.lbl_title.text = "Booking Analytics"
    self.lbl_title.font_size = 24
    self.lbl_title.bold = True

    # Load analytics
    self.load_booking_metrics()
    self.load_booking_trend_chart()
    self.load_peak_hours_heatmap()

  def load_booking_metrics(self):
    """Load booking summary metrics"""
    try:
      result = anvil.server.call('get_booking_stats')

      if result['success']:
        data = result['data']

        # Total bookings
        self.lbl_total.text = f"Total Bookings\n{data['total']:,}"
        self.lbl_total.font_size = 18
        self.lbl_total.bold = True
        self.lbl_total.align = "center"

        # Average booking value
        self.lbl_avg_value.text = f"Avg Booking Value\n${data['avg_value']:,.2f}"
        self.lbl_avg_value.font_size = 16
        self.lbl_avg_value.align = "center"

        # Occupancy rate
        self.lbl_occupancy.text = f"Occupancy Rate\n{data['occupancy_rate']}%"
        self.lbl_occupancy.font_size = 16
        self.lbl_occupancy.align = "center"

        # No-show rate
        self.lbl_no_show.text = f"No-Show Rate\n{data['no_show_rate']}%"
        self.lbl_no_show.font_size = 16
        self.lbl_no_show.foreground = "#FF9800"  # Orange for warning
        self.lbl_no_show.align = "center"

      else:
        alert(f"Error loading metrics: {result.get('error', 'Unknown error')}")

    except Exception as e:
      print(f"Error loading booking metrics: {e}")
      alert(f"Failed to load metrics: {str(e)}")

  def load_booking_trend_chart(self):
    """Load booking rate trend"""
    try:
      result = anvil.server.call('get_booking_trend', months=12)

      if result['success']:
        data = result['data']

        # Create line chart
        self.plot_trend.data = [{
          'type': 'scatter',
          'mode': 'lines+markers',
          'x': [d['month'] for d in data],
          'y': [d['bookings'] for d in data],
          'line': {'color': '#4CAF50', 'width': 3},
          'marker': {'size': 8}
        }]

        self.plot_trend.layout = {
          'title': 'Booking Rate Trend (Last 12 Months)',
          'xaxis': {'title': 'Month'},
          'yaxis': {'title': 'Number of Bookings'},
          'hovermode': 'closest',
          'plot_bgcolor': '#F5F5F5'
        }

      else:
        alert(f"Error loading trend: {result.get('error', 'Unknown error')}")

    except Exception as e:
      print(f"Error loading trend chart: {e}")
      alert(f"Failed to load trend chart: {str(e)}")

  def load_peak_hours_heatmap(self):
    """Load peak hours heatmap"""
    try:
      result = anvil.server.call('get_peak_hours')

      if result['success']:
        data = result['data']

        # Create heatmap
        self.plot_heatmap.data = [{
          'type': 'heatmap',
          'x': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
          'y': [f"{h}:00" for h in range(9, 18)],  # 9 AM to 5 PM
          'z': data['heatmap_values'],  # 2D array: [hours][days]
          'colorscale': 'Greens',
          'hovertemplate': 'Day: %{x}<br>Hour: %{y}<br>Bookings: %{z}<extra></extra>'
        }]

        self.plot_heatmap.layout = {
          'title': 'Peak Hours Heatmap',
          'xaxis': {'title': 'Day of Week', 'side': 'bottom'},
          'yaxis': {'title': 'Hour of Day'},
          'plot_bgcolor': '#FFFFFF'
        }

      else:
        alert(f"Error loading heatmap: {result.get('error', 'Unknown error')}")

    except Exception as e:
      print(f"Error loading heatmap: {e}")
      alert(f"Failed to load heatmap: {str(e)}")
```