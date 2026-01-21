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
def get_customer_activity(user_id):
  """Get customer's activity to determine navigation visibility"""
  user = anvil.users.get_user()

  # Security check
  if not user or user.get_id() != user_id:
    raise Exception("Unauthorized")

  activity = {
    'has_bookings': False,
    'has_orders': False,
    'is_member': False
  }

  try:
    # Check for bookings
    bookings = list(app_tables.tbl_bookings.search(
      customer_id=user
    ))
    activity['has_bookings'] = len(bookings) > 0

    # Check for orders
    orders = list(app_tables.tbl_orders.search(
      customer_id=user
    ))
    activity['has_orders'] = len(orders) > 0

    # Check for membership
    membership = app_tables.tbl_memberships.get(
      customer_id=user,
      status='active'
    )
    activity['is_member'] = membership is not None

  except Exception as e:
    print(f"Error checking customer activity: {e}")

  return activity