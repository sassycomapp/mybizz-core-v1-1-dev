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
def get_booking_stats():
  """
  Get booking summary statistics.
  
  Returns:
    dict: {'success': bool, 'data': dict} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    # Get all bookings
    bookings = list(app_tables.bookings.search())

    if not bookings:
      return {
        'success': True,
        'data': {
          'total': 0,
          'avg_value': 0,
          'occupancy_rate': 0,
          'no_show_rate': 0
        }
      }

    # Total bookings
    total = len(bookings)

    # Average booking value
    total_value = sum(b.get('total_amount', 0) for b in bookings)
    avg_value = total_value / total if total > 0 else 0

    # Occupancy rate (bookings with status 'confirmed' or 'completed')
    confirmed = len([b for b in bookings if b.get('status') in ['confirmed', 'completed']])
    occupancy_rate = round((confirmed / total * 100), 1) if total > 0 else 0

    # No-show rate
    no_shows = len([b for b in bookings if b.get('status') == 'no_show'])
    no_show_rate = round((no_shows / total * 100), 1) if total > 0 else 0

    return {
      'success': True,
      'data': {
        'total': total,
        'avg_value': avg_value,
        'occupancy_rate': occupancy_rate,
        'no_show_rate': no_show_rate
      }
    }

  except Exception as e:
    print(f"Error getting booking stats: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
@anvil.users.login_required
def get_booking_trend(months=12):
  """
  Get booking trend over time.
  
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

    # Get bookings in range
    bookings = list(app_tables.bookings.search(
      created_at=q.greater_than_or_equal_to(start_date)
    ))

    # Group by month
    monthly_data = {}
    for booking in bookings:
      month_key = booking['created_at'].strftime('%Y-%m')
      month_label = booking['created_at'].strftime('%b %Y')

      if month_key not in monthly_data:
        monthly_data[month_key] = {'month': month_label, 'bookings': 0}

      monthly_data[month_key]['bookings'] += 1

    # Sort by date
    result = sorted(monthly_data.values(), key=lambda x: x['month'])

    return {'success': True, 'data': result}

  except Exception as e:
    print(f"Error getting booking trend: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
@anvil.users.login_required
def get_peak_hours():
  """
  Get peak hours heatmap data.
  
  Returns:
    dict: {'success': bool, 'data': dict} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    # Get all bookings
    bookings = list(app_tables.bookings.search())

    # Initialize heatmap grid: [hours 9-17] x [days 0-6]
    heatmap = [[0 for _ in range(7)] for _ in range(9)]  # 9 hours x 7 days

    for booking in bookings:
      if booking.get('booking_date'):
        # Get day of week (0=Monday, 6=Sunday)
        day = booking['booking_date'].weekday()

        # Get hour (assume booking_date includes time)
        hour = booking['booking_date'].hour

        # Only count business hours (9 AM to 5 PM)
        if 9 <= hour <= 17:
          hour_index = hour - 9  # Convert to 0-indexed
          heatmap[hour_index][day] += 1

    return {
      'success': True,
      'data': {
        'heatmap_values': heatmap
      }
    }

  except Exception as e:
    print(f"Error getting peak hours: {e}")
    return {'success': False, 'error': str(e)}
# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#
