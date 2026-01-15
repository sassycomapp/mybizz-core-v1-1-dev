from ._anvil_designer import SubscriptionListFormTemplate
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


class SubscriptionListForm(SubscriptionListFormTemplate):
  """Subscription and recurring payment management"""

  def __init__(self, **properties):
    self.init_components(**properties)

    # Check authentication
    user = anvil.users.get_user()
    if not user:
      open_form('auth.LoginForm')
      return

    if user['role'] not in ['owner', 'manager']:
      alert("Access denied")
      open_form('dashboard.DashboardForm')
      return

    # Configure title
    self.lbl_title.text = "Subscriptions"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True

    # Configure new subscription button
    self.btn_new_subscription.text = "New Subscription"
    self.btn_new_subscription.icon = "fa:plus"
    self.btn_new_subscription.role = "primary-color"

    # Configure filters
    self.dd_status_filter.items = [
      ('All Statuses', 'all'),
      ('Active', 'active'),
      ('Cancelled', 'cancelled'),
      ('Expired', 'expired'),
      ('Trial', 'trial')
    ]
    self.dd_status_filter.selected_value = 'all'

    self.dd_plan_filter.items = [
      ('All Plans', 'all'),
      ('Monthly', 'monthly'),
      ('Annual', 'annual'),
      ('Quarterly', 'quarterly')
    ]
    self.dd_plan_filter.selected_value = 'all'

    # Configure data grid
    self.dg_subscriptions.columns = [
      {'id': 'customer', 'title': 'Customer', 'data_key': 'customer_email', 'width': 200},
      {'id': 'plan', 'title': 'Plan', 'data_key': 'plan_name', 'width': 120},
      {'id': 'amount', 'title': 'Amount', 'data_key': 'amount_display', 'width': 100},
      {'id': 'status', 'title': 'Status', 'data_key': 'status_display', 'width': 100},
      {'id': 'next_bill', 'title': 'Next Bill', 'data_key': 'next_bill_display', 'width': 120},
      {'id': 'actions', 'title': 'Actions', 'data_key': None, 'width': 100}
    ]

    # Load subscriptions
    self.load_subscriptions()

  def load_subscriptions(self):
    """Load subscription data"""
    try:
      filters = {
        'status': self.dd_status_filter.selected_value,
        'plan': self.dd_plan_filter.selected_value
      }

      result = anvil.server.call('get_all_subscriptions', filters)

      if result['success']:
        subscriptions = result['data']

        # Add display fields
        for sub in subscriptions:
          sub['customer_email'] = sub['customer_id']['email'] if sub.get('customer_id') else 'Unknown'
          sub['amount_display'] = f"${sub['amount']:.2f}"

          # Status display
          status_map = {
            'active': '✅ Active',
            'cancelled': '❌ Cancelled',
            'expired': '⏹ Expired',
            'trial': '🆓 Trial'
          }
          sub['status_display'] = status_map.get(sub['status'], sub['status'])

          # Next billing date
          if sub.get('next_billing_date') and sub['status'] == 'active':
            sub['next_bill_display'] = sub['next_billing_date'].strftime('%b %d')
          else:
            sub['next_bill_display'] = '-'

        self.dg_subscriptions.items = subscriptions

        # Calculate stats
        active = len([s for s in subscriptions if s['status'] == 'active'])
        cancelled = len([s for s in subscriptions if s['status'] == 'cancelled'])
        mrr = sum(s['amount'] for s in subscriptions if s['status'] == 'active' and s.get('billing_period') == 'monthly')

        self.lbl_stats.text = f"Active: {active}  •  Cancelled: {cancelled}  •  MRR: ${mrr:.2f}"

      else:
        alert(f"Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
      print(f"Error loading subscriptions: {e}")
      alert(f"Failed to load subscriptions: {str(e)}")

  def button_new_subscription_click(self, **event_args):
    """Create new subscription"""
    alert("Manual subscription creation coming soon!")

  def dropdown_status_filter_change(self, **event_args):
    """Filter by status"""
    self.load_subscriptions()

  def dropdown_plan_filter_change(self, **event_args):
    """Filter by plan"""
    self.load_subscriptions()

  @handle("btn_new_subscription", "click")
  def btn_new_subscription_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("dd_status_filter", "change")
  def dd_status_filter_change(self, **event_args):
    """This method is called when an item is selected"""
    pass

  @handle("dd_plan_filter", "change")
  def dd_plan_filter_change(self, **event_args):
    """This method is called when an item is selected"""
    pass
