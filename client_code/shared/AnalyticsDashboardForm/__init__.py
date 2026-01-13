from ._anvil_designer import AnalyticsDashboardFormTemplate
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


from datetime import datetime, timedelta

class AnalyticsDashboardForm(AnalyticsDashboardFormTemplate):
  """Analytics dashboard with revenue and sales metrics"""

  def __init__(self, **properties):
    self.start_date = None
    self.end_date = None
    self.init_components(**properties)

    # Check permissions
    user = anvil.users.get_user()
    if not user or user['role'] not in ['owner', 'manager']:
      alert("Access denied")
      open_form('dashboard.DashboardForm')
      return

    self.lbl_title.text = "Analytics Dashboard"
    self.lbl_title.font_size = 24
    self.lbl_title.bold = True

    # Date range selector
    self.dd_date_range.items = [
      ('Today', 'today'),
      ('This Week', 'week'),
      ('This Month', 'month'),
      ('Last 30 Days', '30days'),
      ('Last 90 Days', '90days'),
      ('This Year', 'year'),
      ('All Time', 'all')
    ]
    self.dd_date_range.selected_value = 'month'

    # Export button
    self.btn_export.text = "Export Report"
    self.btn_export.icon = "fa:download"
    self.btn_export.role = "outlined-button"

    # Load analytics
    self.load_analytics()

  def get_date_range(self):
    """Get start and end dates based on selection"""
    range_type = self.dd_date_range.selected_value
    now = datetime.now()

    if range_type == 'today':
      start = now.replace(hour=0, minute=0, second=0, microsecond=0)
      end = now
    elif range_type == 'week':
      start = now - timedelta(days=now.weekday())
      end = now
    elif range_type == 'month':
      start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
      end = now
    elif range_type == '30days':
      start = now - timedelta(days=30)
      end = now
    elif range_type == '90days':
      start = now - timedelta(days=90)
      end = now
    elif range_type == 'year':
      start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
      end = now
    else:  # all time
      start = None
      end = None

    return start, end

  def load_analytics(self):
    """Load all analytics data"""
    self.start_date, self.end_date = self.get_date_range()

    try:
      # Load revenue metrics
      self.load_revenue_metrics()

      # Load charts
      self.load_payment_methods_chart()
      self.load_revenue_trend_chart()
      self.load_top_products_chart()
      self.load_top_services_chart()

    except Exception as e:
      alert(f"Failed to load analytics: {str(e)}")

  def load_revenue_metrics(self):
    """Load revenue summary metrics"""
    try:
      result = anvil.server.call('get_revenue_summary', self.start_date, self.end_date)

      if result['success']:
        data = result['data']

        self.lbl_total_revenue.text = f"Total Revenue: ${data['total']:,.2f}"
        self.lbl_total_revenue.font_size = 18
        self.lbl_total_revenue.bold = True

        self.lbl_month_revenue.text = f"This Month: ${data['this_month']:,.2f}"
        self.lbl_month_revenue.font_size = 16

        self.lbl_week_revenue.text = f"This Week: ${data['this_week']:,.2f}"
        self.lbl_week_revenue.font_size = 16

    except Exception as e:
      print(f"Error loading revenue metrics: {e}")

  def load_payment_methods_chart(self):
    """Load payment methods pie chart"""
    try:
      result = anvil.server.call('get_revenue_by_payment_method', self.start_date, self.end_date)

      if result['success']:
        data = result['data']

        # Create pie chart
        self.plot_payment_methods.data = [{
          'type': 'pie',
          'labels': [d['method'] for d in data],
          'values': [d['amount'] for d in data]
        }]

        self.plot_payment_methods.layout = {
          'title': 'Revenue by Payment Method'
        }

    except Exception as e:
      print(f"Error loading payment chart: {e}")

  def load_revenue_trend_chart(self):
    """Load revenue trend line chart"""
    try:
      result = anvil.server.call('get_revenue_trend', months=12)

      if result['success']:
        data = result['data']

        # Create line chart
        self.plot_revenue_trend.data = [{
          'type': 'scatter',
          'mode': 'lines+markers',
          'x': [d['month'] for d in data],
          'y': [d['revenue'] for d in data],
          'line': {'color': '#2196F3'}
        }]

        self.plot_revenue_trend.layout = {
          'title': 'Revenue Trend (12 Months)',
          'xaxis': {'title': 'Month'},
          'yaxis': {'title': 'Revenue ($)'}
        }

    except Exception as e:
      print(f"Error loading trend chart: {e}")

  def load_top_products_chart(self):
    """Load top products bar chart"""
    try:
      result = anvil.server.call('get_top_products', limit=10, start_date=self.start_date, end_date=self.end_date)

      if result['success']:
        data = result['data']

        # Create bar chart
        self.plot_top_products.data = [{
          'type': 'bar',
          'orientation': 'h',
          'x': [d['revenue'] for d in data],
          'y': [d['name'] for d in data],
          'marker': {'color': '#4CAF50'}
        }]

        self.plot_top_products.layout = {
          'title': 'Top Products',
          'xaxis': {'title': 'Revenue ($)'}
        }

    except Exception as e:
      print(f"Error loading products chart: {e}")

  def load_top_services_chart(self):
    """Load top services bar chart"""
    try:
      result = anvil.server.call('get_top_services', limit=10, start_date=self.start_date, end_date=self.end_date)

      if result['success']:
        data = result['data']

        # Create bar chart
        self.plot_top_services.data = [{
          'type': 'bar',
          'orientation': 'h',
          'x': [d['revenue'] for d in data],
          'y': [d['name'] for d in data],
          'marker': {'color': '#FF9800'}
        }]

        self.plot_top_services.layout = {
          'title': 'Top Services',
          'xaxis': {'title': 'Revenue ($)'}
        }

    except Exception as e:
      print(f"Error loading services chart: {e}")

  @handle("dd_date_range", "change")
  def dd_date_range_change(self, **event_args):
    """Reload analytics when date range changes"""
    self.load_analytics()

  def button_export_click(self, **event_args):
    """Export analytics report to CSV"""
    try:
      result = anvil.server.call('export_revenue_report', self.start_date, self.end_date)

      if result['success']:
        # Download CSV
        anvil.media.download(result['csv_file'])
      else:
        alert(f"Export failed: {result.get('error')}")

    except Exception as e:
      alert(f"Failed to export: {str(e)}")

  @handle("btn_export", "click")
  def btn_export_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
