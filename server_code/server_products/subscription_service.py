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

@anvil.server.callable
@anvil.users.login_required
def get_all_subscriptions(filters):
  """
  Get all subscriptions with filters.
  
  Args:
    filters (dict): status, plan
    
  Returns:
    dict: {'success': bool, 'data': list} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    # Build query
    query = {}

    if filters.get('status') and filters['status'] != 'all':
      query['status'] = filters['status']

    if filters.get('plan') and filters['plan'] != 'all':
      query['billing_period'] = filters['plan']

    # Get subscriptions
    subscriptions = list(app_tables.subscriptions.search(
      tables.order_by('created_at', ascending=False),
      **query
    ))

    return {'success': True, 'data': subscriptions}

  except Exception as e:
    print(f"Error getting subscriptions: {e}")
    return {'success': False, 'error': str(e)}