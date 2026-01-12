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
def get_recent_activity(limit=10):
  """
  Get recent activity feed.
  
  Args:
    limit (int): Number of activities to return
    
  Returns:
    dict: {'success': bool, 'data': list} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    # Check permissions
    if user['role'] not in ['owner', 'manager', 'staff']:
      return {'success': False, 'error': 'Access denied'}

    activities = []

    # Get recent bookings
    recent_bookings = list(app_tables.bookings.search(
      tables.order_by('created_at', ascending=False)
    ))[:limit]

    for booking in recent_bookings:
      customer_email = booking['customer_id']['email'] if booking.get('customer_id') else 'Guest'
      resource_name = booking['resource_id']['resource_name'] if booking.get('resource_id') else 'Unknown'

      # Different descriptions based on status
      if booking['status'] == 'checked_out':
        description = f"{customer_email} checked out from {resource_name}"
      else:
        description = f"{customer_email} booked {resource_name}"

      activities.append({
        'type': 'checkout' if booking['status'] == 'checked_out' else 'booking',
        'description': description,
        'timestamp': booking['created_at']
      })

    # Get recent orders
    recent_orders = list(app_tables.orders.search(
      tables.order_by('created_at', ascending=False)
    ))[:limit]

    for order in recent_orders:
      amount = order.get('total_amount', 0)
      activities.append({
        'type': 'order',
        'description': f"New order {order['order_number']} received (${amount:.2f})",
        'timestamp': order['created_at']
      })

    # Get new customers
    recent_customers = list(app_tables.customers.search(
      tables.order_by('created_at', ascending=False)
    ))[:limit]

    for customer in recent_customers:
      activities.append({
        'type': 'customer',
        'description': f"New customer registered: {customer['email']}",
        'timestamp': customer['created_at']
      })

    # Get recent blog posts (if blog module exists)
    try:
      recent_posts = list(app_tables.blog_posts.search(
        status='published',
        tables.order_by('published_at', ascending=False)
      ))[:5]

      for post in recent_posts:
        activities.append({
          'type': 'blog',
          'description': f"Blog post \"{post['title']}\" published",
          'timestamp': post['published_at']
        })
    except:
      pass  # Blog table doesn't exist yet

    # Sort all activities by timestamp
    activities.sort(key=lambda x: x['timestamp'], reverse=True)

    # Return requested limit
    return {'success': True, 'data': activities[:limit]}

  except Exception as e:
    print(f"Error getting recent activity: {e}")
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def get_dashboard_metrics():
  """
  Get dashboard metrics for current user.
  
  Returns:
    dict: {'success': bool, 'data': dict} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    # Check permissions
    if user['role'] not in ['owner', 'manager', 'staff']:
      return {'success': False, 'error': 'Access denied'}

    from datetime import datetime, timedelta

    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    last_week_start = week_start - timedelta(days=7)

    # Today's revenue
    today_orders = list(app_tables.orders.search(
      q.fetch_only('total_amount'),
      created_at=q.greater_than_or_equal_to(datetime.combine(today, datetime.min.time()))
    ))
    today_revenue = sum(o['total_amount'] for o in today_orders if o.get('total_amount'))

    # Yesterday's revenue for comparison
    yesterday = today - timedelta(days=1)
    yesterday_orders = list(app_tables.orders.search(
      q.fetch_only('total_amount'),
      created_at=q.between(
        datetime.combine(yesterday, datetime.min.time()),
        datetime.combine(yesterday, datetime.max.time())
      )
    ))
    yesterday_revenue = sum(o['total_amount'] for o in yesterday_orders if o.get('total_amount'))

    # Calculate revenue change
    if yesterday_revenue > 0:
      revenue_change_pct = ((today_revenue - yesterday_revenue) / yesterday_revenue) * 100
      revenue_change = f"+{revenue_change_pct:.0f}%" if revenue_change_pct > 0 else f"{revenue_change_pct:.0f}%"
    else:
      revenue_change = "+0%"

    # This week's bookings
    week_bookings = len(list(app_tables.bookings.search(
      created_at=q.greater_than_or_equal_to(datetime.combine(week_start, datetime.min.time()))
    )))

    # Last week's bookings
    last_week_bookings = len(list(app_tables.bookings.search(
      created_at=q.between(
        datetime.combine(last_week_start, datetime.min.time()),
        datetime.combine(week_start, datetime.min.time())
      )
    )))

    # Calculate booking change
    if last_week_bookings > 0:
      bookings_change_pct = ((week_bookings - last_week_bookings) / last_week_bookings) * 100
      bookings_change = f"+{bookings_change_pct:.0f}%" if bookings_change_pct > 0 else f"{bookings_change_pct:.0f}%"
    else:
      bookings_change = "+0%"

    # New customers this week
    new_customers = len(list(app_tables.customers.search(
      created_at=q.greater_than_or_equal_to(datetime.combine(week_start, datetime.min.time()))
    )))

    # Pending tasks (bookings pending confirmation)
    pending_tasks = len(list(app_tables.bookings.search(
      status='pending'
    )))

    return {
      'success': True,
      'data': {
        'today_revenue': today_revenue,
        'revenue_change': revenue_change,
        'week_bookings': week_bookings,
        'bookings_change': bookings_change,
        'new_customers': new_customers,
        'customers_change': f"+{new_customers}",
        'pending_tasks': pending_tasks
      }
    }

  except Exception as e:
    print(f"Error getting dashboard metrics: {e}")
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def get_storage_usage():
  """
  Get storage usage statistics.
  
  Returns:
    dict: {'success': bool, 'data': dict} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    # Check permissions
    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    # Count database rows across all tables
    total_rows = 0

    tables_to_check = [
      app_tables.bookings,
      app_tables.customers,
      app_tables.products,
      app_tables.orders,
      app_tables.order_items,
      app_tables.services,
      app_tables.reviews,
      app_tables.blog_posts
    ]

    for table in tables_to_check:
      try:
        table_rows = len(list(table.search()))
        total_rows += table_rows
      except Exception as e:
        # Table might not exist yet
        print(f"Could not count rows in table: {e}")
        pass

    # Calculate media storage
    # Note: This is an approximation - actual calculation requires
    # iterating through all media columns
    media_bytes = 0

    # TODO: Implement actual media calculation by checking media columns
    # For now, return 0

    # Anvil Hobby Plan limits
    database_limit = 150000  # rows
    media_limit_bytes = 10 * 1024 * 1024 * 1024  # 10 GB

    return {
      'success': True,
      'data': {
        'database_rows': total_rows,
        'database_limit': database_limit,
        'media_bytes': media_bytes,
        'media_limit_bytes': media_limit_bytes
      }
    }

  except Exception as e:
    print(f"Error getting storage usage: {e}")
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def get_detailed_storage_report():
  """
  Get detailed breakdown of storage by table.
  
  Returns:
    dict: {'success': bool, 'data': dict} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    # Check permissions
    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    table_counts = {}
    total_rows = 0

    # Define all tables to check
    tables_map = {
      'bookings': app_tables.bookings,
      'customers': app_tables.customers,
      'products': app_tables.products,
      'orders': app_tables.orders,
      'order_items': app_tables.order_items,
      'services': app_tables.services,
      'reviews': app_tables.reviews,
      'blog_posts': app_tables.blog_posts,
      'tickets': app_tables.tickets,
      'ticket_messages': app_tables.ticket_messages
    }

    for table_name, table in tables_map.items():
      try:
        count = len(list(table.search()))
        table_counts[table_name] = count
        total_rows += count
      except Exception as e:
        # Table doesn't exist yet
        table_counts[table_name] = 0

    return {
      'success': True,
      'data': {
        'table_counts': table_counts,
        'total_rows': total_rows
      }
    }

  except Exception as e:
    print(f"Error getting detailed report: {e}")
    return {'success': False, 'error': str(e)}