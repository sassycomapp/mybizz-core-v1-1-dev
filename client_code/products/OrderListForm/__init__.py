from ._anvil_designer import OrderListFormTemplate
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


class OrderListForm(OrderListFormTemplate):
  """Admin order management"""

  def __init__(self, **properties):
    self.init_components(**properties)

    # Check authentication
    user = anvil.users.get_user()
    if not user:
      open_form('auth.LoginForm')
      return

    if user['role'] not in ['owner', 'manager', 'staff']:
      alert("Access denied")
      open_form('dashboard.DashboardForm')
      return

    # Configure title
    self.lbl_title.text = "Orders"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True

    # Configure search
    self.txt_search.placeholder = "Search by order # or customer email..."
    self.txt_search.icon = "fa:search"

    self.btn_search.text = ""
    self.btn_search.icon = "fa:search"
    self.btn_search.role = "secondary-color"

    # Configure filters
    self.dd_status_filter.items = [
      ('All Statuses', 'all'),
      ('Pending', 'pending'),
      ('Processing', 'processing'),
      ('Shipped', 'shipped'),
      ('Completed', 'completed'),
      ('Cancelled', 'cancelled'),
      ('Refunded', 'refunded')
    ]
    self.dd_status_filter.selected_value = 'all'

    self.dd_date_filter.items = [
      ('All Time', 'all'),
      ('Today', 'today'),
      ('This Week', 'week'),
      ('This Month', 'month'),
      ('This Year', 'year')
    ]
    self.dd_date_filter.selected_value = 'all'

    # Configure data grid
    self.dg_orders.columns = [
      {'id': 'order_number', 'title': 'Order #', 'data_key': 'order_number', 'width': 150},
      {'id': 'customer', 'title': 'Customer', 'data_key': 'customer_email', 'width': 200},
      {'id': 'total', 'title': 'Total', 'data_key': 'total_display', 'width': 100},
      {'id': 'status', 'title': 'Status', 'data_key': 'status_display', 'width': 120},
      {'id': 'date', 'title': 'Date', 'data_key': 'date_display', 'width': 120},
      {'id': 'actions', 'title': 'Actions', 'data_key': None, 'width': 100}
    ]

    # Configure stats
    self.lbl_stats.font_size = 12
    self.lbl_stats.foreground = "#666666"

    # Load orders
    self.load_orders()

  def load_orders(self):
    """Load orders with filters"""
    try:
      filters = {
        'search': self.txt_search.text,
        'status': self.dd_status_filter.selected_value,
        'date_range': self.dd_date_filter.selected_value
      }

      result = anvil.server.call('get_all_orders_filtered', filters)

      if result['success']:
        orders = result['data']

        # Add display fields
        for order in orders:
          # Total display
          order['total_display'] = f"${order['total_amount']:.2f}"

          # Status display with emoji
          status_map = {
            'pending': '⏳ Pending',
            'processing': '📦 Processing',
            'shipped': '🚚 Shipped',
            'completed': '✅ Completed',
            'cancelled': '❌ Cancelled',
            'refunded': '💰 Refunded'
          }
          order['status_display'] = status_map.get(order['status'], order['status'])

          # Date display
          order['date_display'] = order['created_at'].strftime('%b %d')

          # Customer email
          order['customer_email'] = order['customer_id']['email'] if order.get('customer_id') else 'Guest'

        self.dg_orders.items = orders

        # Update stats
        total = len(orders)
        pending = len([o for o in orders if o['status'] == 'pending'])
        revenue = sum(o['total_amount'] for o in orders if o['payment_status'] == 'paid')

        self.lbl_stats.text = f"Total: {total} orders  •  Pending: {pending}  •  Revenue: ${revenue:,.2f}"

      else:
        alert(f"Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
      print(f"Error loading orders: {e}")
      alert(f"Failed to load orders: {str(e)}")

  def button_search_click(self, **event_args):
    """Search orders"""
    self.load_orders()

  def dropdown_status_filter_change(self, **event_args):
    """Filter by status"""
    self.load_orders()

  def dropdown_date_filter_change(self, **event_args):
    """Filter by date"""
    self.load_orders()

  @handle("btn_search", "click")
  def btn_search_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("dd_status_filter", "change")
  def dd_status_filter_change(self, **event_args):
    """This method is called when an item is selected"""
    pass

  @handle("dd_date_filter", "change")
  def dd_date_filter_change(self, **event_args):
    """This method is called when an item is selected"""
    pass
