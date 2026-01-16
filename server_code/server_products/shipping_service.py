import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.stripe
import anvil.secrets
import anvil.files
from anvil.files import data_files
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime
#from .bobgo_service import ... (Import is not complete in this state)
#from .easyship_service import ...(Import is not complete in this state)


@anvil.server.callable
@anvil.users.login_required
def get_unshipped_orders():
  """Get orders that haven't been shipped"""
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager', 'staff']:
      return {'success': False, 'error': 'Access denied'}

    # Get orders with status 'paid' or 'processing' (not shipped yet)
    orders = list(app_tables.orders.search(
      status=q.any_of('paid', 'processing')
    ))

    # Add customer email for display
    for order in orders:
      if order.get('customer_id'):
        order['customer_email'] = order['customer_id']['email']
      else:
        order['customer_email'] = 'Guest'

    return {'success': True, 'data': orders}

  except Exception as e:
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def create_manual_shipment(shipment_data):
  """Create manual shipment entry"""
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager', 'staff']:
      return {'success': False, 'error': 'Access denied'}

    order_id = shipment_data['order_id']
    order = app_tables.orders.get_by_id(order_id)

    if not order:
      return {'success': False, 'error': 'Order not found'}

    # Update order status
    order['status'] = 'shipped'
    order['updated_at'] = datetime.now()
    order.update()

    # TODO: Create shipment record in shipments table
    # TODO: Send shipping notification email

    return {'success': True}

  except Exception as e:
    return {'success': False, 'error': str(e)}