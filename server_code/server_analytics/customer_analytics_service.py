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
from datetime import datetime, timedelta

@anvil.server.callable
@anvil.users.login_required
def get_customer_metrics():
  """
  Get customer summary statistics.
  
  Returns:
    dict: {'success': bool, 'data': dict} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    # Get all customers (users with role 'customer')
    customers = list(app_tables.users.search(role='customer'))

    if not customers:
      return {
        'success': True,
        'data': {
          'total': 0,
          'new_this_month': 0,
          'avg_ltv': 0,
          'repeat_rate': 0
        }
      }

    # Total customers
    total = len(customers)

    # New customers this month
    start_of_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    new_this_month = len([
      c for c in customers 
      if c.get('created_at') and c['created_at'] >= start_of_month
    ])

    # Calculate average lifetime value (from orders)
    total_ltv = 0
    for customer in customers:
      orders = list(app_tables.orders.search(customer_id=customer))
      customer_ltv = sum(o.get('total_amount', 0) for o in orders)
      total_ltv += customer_ltv

    avg_ltv = total_ltv / total if total > 0 else 0

    # Calculate repeat customer rate
    repeat_customers = 0
    for customer in customers:
      order_count = len(list(app_tables.orders.search(customer_id=customer)))
      if order_count > 1:
        repeat_customers += 1

    repeat_rate = round((repeat_customers / total * 100), 1) if total > 0 else 0

    return {
      'success': True,
      'data': {
        'total': total,
        'new_this_month': new_this_month,
        'avg_ltv': avg_ltv,
        'repeat_rate': repeat_rate
      }
    }

  except Exception as e:
    print(f"Error getting customer metrics: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
@anvil.users.login_required
def get_customer_acquisition_trend(months=12):
  """
  Get customer acquisition trend over time.
  
  Args:
    months (int): Number of months to look back
    
  Returns:
    dict: {'success': bool, 'data': list} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=months * 30)

    # Get customers in range
    customers = list(app_tables.users.search(
      role='customer',
      created_at=q.greater_than_or_equal_to(start_date)
    ))

    # Group by month
    monthly_data = {}
    for customer in customers:
      if customer.get('created_at'):
        month_key = customer['created_at'].strftime('%Y-%m')
        month_label = customer['created_at'].strftime('%b %Y')

        if month_key not in monthly_data:
          monthly_data[month_key] = {'month': month_label, 'new_customers': 0}

        monthly_data[month_key]['new_customers'] += 1

    # Sort by date
    result = sorted(monthly_data.values(), key=lambda x: x['month'])

    return {'success': True, 'data': result}

  except Exception as e:
    print(f"Error getting customer acquisition trend: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
@anvil.users.login_required
def get_customer_distribution():
  """
  Get customer distribution by business vertical.
  
  Returns:
    dict: {'success': bool, 'data': list} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    # Get all customers
    customers = list(app_tables.users.search(role='customer'))

    if not customers:
      return {'success': True, 'data': []}

    total_customers = len(customers)

    # Count customers by primary activity
    # (Determine by which table they interact with most)
    distribution = {
      'Bookings': 0,
      'Products': 0,
      'Services': 0
    }

    for customer in customers:
      # Count activities in each vertical
      booking_count = len(list(app_tables.bookings.search(customer_id=customer)))
      order_count = len(list(app_tables.orders.search(customer_id=customer)))

      # Assign to primary vertical based on activity
      if booking_count > order_count:
        distribution['Bookings'] += 1
      elif order_count > 0:
        distribution['Products'] += 1
      else:
        distribution['Services'] += 1  # Default for customers with no activity

    # Format results
    result = []
    for vertical, count in distribution.items():
      percentage = round((count / total_customers * 100), 1) if total_customers > 0 else 0
      result.append({
        'vertical': vertical,
        'count': count,
        'percentage': percentage
      })

    return {'success': True, 'data': result}

  except Exception as e:
    print(f"Error getting customer distribution: {e}")
    return {'success': False, 'error': str(e)}