from ._anvil_designer import CustomerAnalyticsFormTemplate
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


class CustomerAnalyticsForm(CustomerAnalyticsFormTemplate):
  """Customer analytics dashboard"""

  def __init__(self, **properties):
    self.init_components(**properties)

    # Check permissions
    user = anvil.users.get_user()
    if not user or user['role'] not in ['owner', 'manager']:
      alert("Access denied")
      open_form('dashboard.DashboardForm')
      return

    # Configure title
    self.lbl_title.text = "Customer Analytics"
    self.lbl_title.font_size = 24
    self.lbl_title.bold = True

    # Load analytics
    self.load_customer_metrics()
    self.load_acquisition_chart()
    self.load_distribution_chart()

  def load_customer_metrics(self):
    """Load customer summary metrics"""
    try:
      result = anvil.server.call('get_customer_metrics')

      if result['success']:
        data = result['data']

        # Total customers
        self.lbl_total.text = f"Total Customers\n{data['total']:,}"
        self.lbl_total.font_size = 18
        self.lbl_total.bold = True
        self.lbl_total.align = "center"

        # New this month
        self.lbl_new_month.text = f"New This Month\n{data['new_this_month']}"
        self.lbl_new_month.font_size = 16
        self.lbl_new_month.align = "center"

        # Average lifetime value
        self.lbl_ltv.text = f"Avg Lifetime Value\n${data['avg_ltv']:,.2f}"
        self.lbl_ltv.font_size = 16
        self.lbl_ltv.align = "center"

        # Repeat customer rate
        self.lbl_repeat_rate.text = f"Repeat Customer Rate\n{data['repeat_rate']}%"
        self.lbl_repeat_rate.font_size = 16
        self.lbl_repeat_rate.align = "center"

      else:
        alert(f"Error loading metrics: {result.get('error', 'Unknown error')}")

    except Exception as e:
      print(f"Error loading customer metrics: {e}")
      alert(f"Failed to load metrics: {str(e)}")

  def load_acquisition_chart(self):
    """Load customer acquisition trend"""
    try:
      result = anvil.server.call('get_customer_acquisition_trend', months=12)

      if result['success']:
        data = result['data']

        # Create line chart
        self.plot_acquisition.data = [{
          'type': 'scatter',
          'mode': 'lines+markers',
          'x': [d['month'] for d in data],
          'y': [d['new_customers'] for d in data],
          'line': {'color': '#2196F3', 'width': 3},
          'marker': {'size': 8}
        }]

        self.plot_acquisition.layout = {
          'title': 'Customer Acquisition Trend (Last 12 Months)',
          'xaxis': {'title': 'Month'},
          'yaxis': {'title': 'New Customers'},
          'hovermode': 'closest',
          'plot_bgcolor': '#F5F5F5'
        }

      else:
        alert(f"Error loading trend: {result.get('error', 'Unknown error')}")

    except Exception as e:
      print(f"Error loading acquisition chart: {e}")
      alert(f"Failed to load acquisition chart: {str(e)}")

  def load_distribution_chart(self):
    """Load customer distribution by vertical"""
    try:
      result = anvil.server.call('get_customer_distribution')

      if result['success']:
        data = result['data']

        # Create bar chart
        self.plot_distribution.data = [{
          'type': 'bar',
          'x': [d['vertical'] for d in data],
          'y': [d['count'] for d in data],
          'marker': {'color': '#4CAF50'},
          'text': [d['percentage'] for d in data],
          'textposition': 'auto',
          'hovertemplate': '%{x}: %{y} customers (%{text}%)<extra></extra>'
        }]

        self.plot_distribution.layout = {
          'title': 'Customer Distribution by Vertical',
          'xaxis': {'title': 'Business Vertical'},
          'yaxis': {'title': 'Number of Customers'},
          'plot_bgcolor': '#F5F5F5'
        }

      else:
        alert(f"Error loading distribution: {result.get('error', 'Unknown error')}")

    except Exception as e:
      print(f"Error loading distribution chart: {e}")
      alert(f"Failed to load distribution chart: {str(e)}")