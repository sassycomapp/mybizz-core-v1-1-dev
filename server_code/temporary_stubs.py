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


# Temporary stub - will be moved to server_code/auth/service.py later
@anvil.server.callable
def create_account(email, password, business_name):
  """Create new user account with owner role"""
  try:
    # Create user using Anvil Users
    user = anvil.users.signup_with_email(email, password)

    # Set custom fields
    user['role'] = 'owner'
    user['account_status'] = 'active'
    user['created_at'] = datetime.now()
    user.update()

    # TODO: Create business profile, config, theme (Task T1.4-010)

    return {'success': True, 'user_id': user.get_id()}

  except anvil.users.UserExists:
    return {'success': False, 'error': 'Email already registered'}
  except Exception as e:
    print(f"Error creating account: {e}")
    return {'success': False, 'error': str(e)}

#*****

@anvil.server.callable
def get_all_blog_posts(status_filter='all', search_term=None):
  """Get all blog posts for admin"""
  try:
    user = anvil.users.get_user()
    if not user:
      return []

    # Build query
    query = {'client_id': user}

    if status_filter != 'all':
      query['status'] = status_filter

    # Search by title if provided
    posts = app_tables.tbl_blog_posts.search(**query)

    if search_term:
      posts = [p for p in posts if search_term.lower() in p['title'].lower()]

    return list(posts)

  except Exception as e:
    print(f"Error getting blog posts: {e}")
    return []

@anvil.server.callable
def delete_blog_post(post_id):
  """Delete a blog post"""
  try:
    user = anvil.users.get_user()
    post = app_tables.tbl_blog_posts.get_by_id(post_id)

    if post and post['client_id'] == user:
      post.delete()
      return {'success': True}
    else:
      return {'success': False, 'error': 'Post not found'}

  except Exception as e:
    print(f"Error deleting post: {e}")
    return {'success': False, 'error': str(e)}

    #*****

    @anvil.server.callable
    def get_blog_categories():
      """Get all blog categories"""
  user = anvil.users.get_user()
  return list(app_tables.tbl_blog_categories.search(client_id=user))

@anvil.server.callable
def get_blog_post(post_id):
  """Get single blog post"""
  user = anvil.users.get_user()
  post = app_tables.tbl_blog_posts.get_by_id(post_id)

  if post and post['client_id'] == user:
    return post
  return None

@anvil.server.callable
def save_blog_post(post_id, post_data):
  """Save or update blog post"""
  try:
    user = anvil.users.get_user()

    if post_id:
      # Update existing
      post = app_tables.tbl_blog_posts.get_by_id(post_id)
      if post and post['client_id'] == user:
        post.update(**post_data)
        if post_data['status'] == 'published' and not post['published_at']:
          post['published_at'] = datetime.now()
    else:
      # Create new
      post_data['client_id'] = user
      post_data['author_id'] = user
      post_data['view_count'] = 0
      post_data['created_at'] = datetime.now()

      if post_data['status'] == 'published':
        post_data['published_at'] = datetime.now()

      app_tables.tbl_blog_posts.add_row(**post_data)

    return {'success': True}

  except Exception as e:
    print(f"Error saving post: {e}")
    return {'success': False, 'error': str(e)}

*****

@anvil.server.callable
def get_all_blog_posts(status_filter='all', search_term=None):
  """Get all blog posts for admin"""
  try:
    user = anvil.users.get_user()
    if not user:
      return []

    # Build query
    query = {'client_id': user}

    if status_filter != 'all':
      query['status'] = status_filter

    # Search by title if provided
    posts = app_tables.tbl_blog_posts.search(**query)

    if search_term:
      posts = [p for p in posts if search_term.lower() in p['title'].lower()]

    return list(posts)

  except Exception as e:
    print(f"Error getting blog posts: {e}")
    return []

@anvil.server.callable
def delete_blog_post(post_id):
  """Delete a blog post"""
  try:
    user = anvil.users.get_user()
    post = app_tables.tbl_blog_posts.get_by_id(post_id)

    if post and post['client_id'] == user:
      post.delete()
      return {'success': True}
    else:
      return {'success': False, 'error': 'Post not found'}

  except Exception as e:
    print(f"Error deleting post: {e}")
    return {'success': False, 'error': str(e)}

    *****

    @anvil.server.callable
    def get_public_blog_post(slug):
      """Get published post by slug and increment view count"""
  try:
    post = app_tables.tbl_blog_posts.get(
      slug=slug,
      status='published'
    )

    if not post:
      return None

    # Increment view count
    post['view_count'] = (post['view_count'] or 0) + 1
    post.update()

    # Add author name
    if post.get('author_id'):
      post['author_name'] = post['author_id']['email'].split('@')[0]

    # Add category name
    if post.get('category_id'):
      post['category_name'] = post['category_id']['name']
    else:
      post['category_name'] = 'Uncategorized'

    return post

  except Exception as e:
    print(f"Error getting post: {e}")
    return None

    *****

    @anvil.server.callable
    def get_blog_category(category_id):
      """Get single category"""
  user = anvil.users.get_user()
  category = app_tables.tbl_blog_categories.get_by_id(category_id)

  if category and category['client_id'] == user:
    return category
  return None

@anvil.server.callable
def save_blog_category(category_id, category_data):
  """Save or update blog category"""
  try:
    user = anvil.users.get_user()

    if category_id:
      # Update existing
      category = app_tables.tbl_blog_categories.get_by_id(category_id)
      if category and category['client_id'] == user:
        category.update(**category_data)
    else:
      # Create new
      category_data['client_id'] = user
      app_tables.tbl_blog_categories.add_row(**category_data)

    return {'success': True}

  except Exception as e:
    print(f"Error saving category: {e}")
    return {'success': False, 'error': str(e)}

@anvil.server.callable
def delete_blog_category(category_id):
  """Delete a blog category"""
  try:
    user = anvil.users.get_user()
    category = app_tables.tbl_blog_categories.get_by_id(category_id)

    if category and category['client_id'] == user:
      # Check if any posts use this category
      posts_count = len(list(
        app_tables.tbl_blog_posts.search(category_id=category)
      ))

      if posts_count > 0:
        return {'success': False, 'error': f'{posts_count} posts use this category'}

      category.delete()
      return {'success': True}
    else:
      return {'success': False, 'error': 'Category not found'}

  except Exception as e:
    print(f"Error deleting category: {e}")
    return {'success': False, 'error': str(e)}

    *****

@anvil.server.callable
def get_public_blog_categories():
  """Get categories that have published posts"""
  # Get all categories with at least one published post
  categories = []
  for cat in app_tables.tbl_blog_categories.search():
    posts_count = len(list(
      app_tables.tbl_blog_posts.search(
        category_id=cat,
        status='published'
      )
    ))
    if posts_count > 0:
      categories.append(cat)

  return categories

@anvil.server.callable
def get_public_blog_posts(category_id=None, search_term=None):
  """Get published blog posts"""
  query = {'status': 'published'}

  if category_id:
    category = app_tables.tbl_blog_categories.get_by_id(category_id)
    query['category_id'] = category

  posts = list(app_tables.tbl_blog_posts.search(
    tables.order_by('published_at', ascending=False),
    **query
  ))

  # Search filter
  if search_term:
    search_lower = search_term.lower()
    posts = [
      p for p in posts 
      if search_lower in p['title'].lower() or 
      search_lower in (p.get('excerpt', '') or '').lower()
    ]

  # Add category name for display
  for post in posts:
    if post.get('category_id'):
      post['category_name'] = post['category_id']['name']
    else:
      post['category_name'] = 'Uncategorized'

  return posts

*****

@anvil.server.callable
def get_available_appointment_slots(staff_id, date, duration_minutes):
  """Get available appointment slots for staff on date"""
  try:
    # Get staff availability
    day_of_week = date.weekday()

    # If staff_id provided, check their schedule
    if staff_id:
      staff = app_tables.users.get_by_id(staff_id)
      # For now, use standard business hours
      start_hour, end_hour = 9, 17  # 9 AM to 5 PM
    else:
      start_hour, end_hour = 9, 17

    # Generate slots
    slots = []
    current_hour = start_hour

    while current_hour < end_hour:
      slot_time = f"{current_hour:02d}:00"
      slot_datetime = datetime.combine(date, datetime.min.time()).replace(hour=current_hour)

      # Check if slot is available (not booked)
      is_available = len(list(app_tables.tbl_bookings.search(
        staff_id=staff if staff_id else None,
        start_datetime=slot_datetime,
        status=q.any_of('pending', 'confirmed')
      ))) == 0

      if is_available:
        slots.append({
          'time': slot_time,
          'time_display': datetime.strptime(slot_time, '%H:%M').strftime('%I:%M %p')
        })

      current_hour += 1

    return slots

  except Exception as e:
    print(f"Error getting appointment slots: {e}")
    return []

@anvil.server.callable
def schedule_appointment(appointment_data):
  """Schedule new appointment"""
  try:
    user = anvil.users.get_user()

    # Get related records
    customer = app_tables.users.get_by_id(appointment_data['customer_id'])
    service = app_tables.tbl_services.get_by_id(appointment_data['service_id'])

    staff = None
    if appointment_data.get('staff_id'):
      staff = app_tables.users.get_by_id(appointment_data['staff_id'])

    # Create booking
    booking = app_tables.tbl_bookings.add_row(
      client_id=user,
      customer_id=customer,
      service_id=service,
      staff_id=staff,
      booking_type='appointment',
      start_datetime=appointment_data['start_datetime'],
      end_datetime=appointment_data['end_datetime'],
      status='confirmed',
      total_amount=appointment_data['total_amount'],
      metadata={
        'meeting_type': appointment_data['meeting_type'],
        'client_notes': appointment_data.get('client_notes', '')
      },
      created_at=datetime.now(),
      booking_number=f"APT-{datetime.now().strftime('%Y%m%d')}-{len(list(app_tables.tbl_bookings.search()))+1:03d}"
    )

    # TODO: Send confirmation email
    # TODO: Create calendar event

    return {'success': True, 'booking_id': booking.get_id()}

  except Exception as e:
    print(f"Error scheduling appointment: {e}")
    return {'success': False, 'error': str(e)}

*****

@anvil.server.callable
def get_available_appointment_slots(staff_id, date, duration_minutes):
  """Get available appointment slots for staff on date"""
  try:
    # Get staff availability
    day_of_week = date.weekday()

    # If staff_id provided, check their schedule
    if staff_id:
      staff = app_tables.users.get_by_id(staff_id)
      # For now, use standard business hours
      start_hour, end_hour = 9, 17  # 9 AM to 5 PM
    else:
      start_hour, end_hour = 9, 17

    # Generate slots
    slots = []
    current_hour = start_hour

    while current_hour < end_hour:
      slot_time = f"{current_hour:02d}:00"
      slot_datetime = datetime.combine(date, datetime.min.time()).replace(hour=current_hour)

      # Check if slot is available (not booked)
      is_available = len(list(app_tables.tbl_bookings.search(
        staff_id=staff if staff_id else None,
        start_datetime=slot_datetime,
        status=q.any_of('pending', 'confirmed')
      ))) == 0

      if is_available:
        slots.append({
          'time': slot_time,
          'time_display': datetime.strptime(slot_time, '%H:%M').strftime('%I:%M %p')
        })

      current_hour += 1

    return slots

  except Exception as e:
    print(f"Error getting appointment slots: {e}")
    return []

@anvil.server.callable
def schedule_appointment(appointment_data):
  """Schedule new appointment"""
  try:
    user = anvil.users.get_user()

    # Get related records
    customer = app_tables.users.get_by_id(appointment_data['customer_id'])
    service = app_tables.tbl_services.get_by_id(appointment_data['service_id'])

    staff = None
    if appointment_data.get('staff_id'):
      staff = app_tables.users.get_by_id(appointment_data['staff_id'])

    # Create booking
    booking = app_tables.tbl_bookings.add_row(
      client_id=user,
      customer_id=customer,
      service_id=service,
      staff_id=staff,
      booking_type='appointment',
      start_datetime=appointment_data['start_datetime'],
      end_datetime=appointment_data['end_datetime'],
      status='confirmed',
      total_amount=appointment_data['total_amount'],
      metadata={
        'meeting_type': appointment_data['meeting_type'],
        'client_notes': appointment_data.get('client_notes', '')
      },
      created_at=datetime.now(),
      booking_number=f"APT-{datetime.now().strftime('%Y%m%d')}-{len(list(app_tables.tbl_bookings.search()))+1:03d}"
    )

    # TODO: Send confirmation email
    # TODO: Create calendar event

    return {'success': True, 'booking_id': booking.get_id()}

  except Exception as e:
    print(f"Error scheduling appointment: {e}")
    return {'success': False, 'error': str(e)}

*****

@anvil.server.callable
def get_booking_analytics(days):
  """Get booking analytics for specified days"""
  try:
    user = anvil.users.get_user()

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # Get bookings in range
    bookings = list(app_tables.tbl_bookings.search(
      client_id=user
    ))

    # Filter by date
    current_bookings = [
      b for b in bookings
      if start_date <= b['start_datetime'] <= end_date
    ]

    # Previous period for comparison
    prev_start = start_date - timedelta(days=days)
    prev_bookings = [
      b for b in bookings
      if prev_start <= b['start_datetime'] < start_date
    ]

    # Calculate stats
    total_bookings = len(current_bookings)
    prev_total = len(prev_bookings)
    bookings_change = f"+{int((total_bookings - prev_total) / prev_total * 100) if prev_total > 0 else 0}%"

    total_revenue = sum(b.get('total_amount', 0) for b in current_bookings)
    prev_revenue = sum(b.get('total_amount', 0) for b in prev_bookings)
    revenue_change = f"+{int((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue > 0 else 0}%"

    no_shows = len([b for b in current_bookings if b['status'] == 'no_show'])

    avg_value = total_revenue / total_bookings if total_bookings > 0 else 0

    # Top resources
    resource_counts = {}
    for booking in current_bookings:
      if booking.get('resource_id'):
        resource_name = booking['resource_id']['resource_name']
        resource_counts[resource_name] = resource_counts.get(resource_name, 0) + 1

    top_resources = [
      {
        'rank': i + 1,
        'resource_name': name,
        'booking_count': count
      }
      for i, (name, count) in enumerate(
        sorted(resource_counts.items(), key=lambda x: x[1], reverse=True)[:5]
      )
    ]

    # Peak times
    time_counts = {}
    for booking in current_bookings:
      hour = booking['start_datetime'].hour
      time_str = f"{hour:02d}:00"
      time_counts[time_str] = time_counts.get(time_str, 0) + 1

    peak_times = [
      {'time': time, 'count': count}
      for time, count in sorted(time_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    ]

    return {
      'total_bookings': total_bookings,
      'bookings_change': bookings_change,
      'total_revenue': total_revenue,
      'revenue_change': revenue_change,
      'no_shows': no_shows,
      'noshows_change': '0%',
      'avg_booking_value': avg_value,
      'avg_change': '+0%',
      'top_resources': top_resources,
      'peak_times': peak_times
    }

  except Exception as e:
    print(f"Error getting analytics: {e}")
    return {}

*****

@anvil.server.callable
def get_all_bookable_resources():
  """Get all bookable resources"""
  user = anvil.users.get_user()
  return list(app_tables.tbl_bookable_resources.search(
    client_id=user,
    is_active=True
  ))

@anvil.server.callable
def get_bookings_for_calendar(start_date, end_date, resource_id=None):
  """Get bookings for calendar date range"""
  user = anvil.users.get_user()

  query = {
    'client_id': user
  }

  if resource_id:
    resource = app_tables.tbl_bookable_resources.get_by_id(resource_id)
    query['resource_id'] = resource

  # Get bookings in date range
  bookings = list(app_tables.tbl_bookings.search(
    **query
  ))

  # Filter by date range (Anvil doesn't support date range queries easily)
  filtered = [
    b for b in bookings
    if start_date <= b['start_datetime'] < end_date
  ]

  # Add denormalized data for display
  for booking in filtered:
    if booking.get('customer_id'):
      booking['customer_name'] = booking['customer_id']['email'].split('@')[0]
    else:
      booking['customer_name'] = 'Guest'

    if booking.get('resource_id'):
      booking['resource_name'] = booking['resource_id']['resource_name']
    else:
      booking['resource_name'] = 'Unknown'

  return filtered

*****

@anvil.server.callable
def get_all_customers():
  """Get all customers for dropdown"""
  user = anvil.users.get_user()
  return list(app_tables.users.search(
    role='customer',
    account_status='active'
  ))

@anvil.server.callable
def get_booking_metadata_schema(booking_type):
  """Get metadata schema for booking type"""
  schema = app_tables.tbl_booking_metadata_schemas.get(
    booking_type=booking_type
  )
  return dict(schema) if schema else None

@anvil.server.callable
def check_availability(resource_id, start_datetime, end_datetime, exclude_booking_id=None):
  """Check if resource is available for time slot"""
  try:
    resource = app_tables.tbl_bookable_resources.get_by_id(resource_id)

    # Check for overlapping bookings
    overlapping = list(app_tables.tbl_bookings.search(
      resource_id=resource,
      status=q.any_of('pending', 'confirmed')
    ))

    # Filter by datetime overlap
    for booking in overlapping:
      if exclude_booking_id and booking.get_id() == exclude_booking_id:
        continue

      if (start_datetime < booking['end_datetime'] and 
          end_datetime > booking['start_datetime']):
        return {
          'available': False,
          'reason': f"Conflicts with booking {booking['booking_number']}"
        }

    return {'available': True}

  except Exception as e:
    print(f"Error checking availability: {e}")
    return {'available': False, 'reason': str(e)}

@anvil.server.callable
def get_booking(booking_id):
  """Get single booking"""
  booking = app_tables.tbl_bookings.get_by_id(booking_id)
  return booking

@anvil.server.callable
def save_booking(booking_id, booking_data):
  """Save or update booking"""
  try:
    user = anvil.users.get_user()

    if booking_id:
      # Update existing
      booking = app_tables.tbl_bookings.get_by_id(booking_id)
      booking.update(**booking_data)
    else:
      # Create new
      booking_data['client_id'] = user
      booking_data['created_at'] = datetime.now()

      # Generate booking number
      count = len(list(app_tables.tbl_bookings.search(client_id=user)))
      booking_data['booking_number'] = f"BK-{datetime.now().strftime('%Y%m%d')}-{count+1:03d}"

      app_tables.tbl_bookings.add_row(**booking_data)

    return {'success': True}

  except Exception as e:
    print(f"Error saving booking: {e}")
    return {'success': False, 'error': str(e)}

*****

@anvil.server.callable
def get_all_bookings(filters):
  """Get all bookings with filters"""
  user = anvil.users.get_user()

  query = {'client_id': user}

  # Status filter
  if filters.get('status'):
    query['status'] = filters['status']

  # Resource filter
  if filters.get('resource_id'):
    resource = app_tables.tbl_bookable_resources.get_by_id(filters['resource_id'])
    query['resource_id'] = resource

  # Get bookings
  bookings = list(app_tables.tbl_bookings.search(
    tables.order_by('start_datetime', ascending=False),
    **query
  ))

  # Date range filter (client-side for now)
  if filters.get('date_from') and filters.get('date_to'):
    date_from = filters['date_from']
    date_to = filters['date_to']
    bookings = [
      b for b in bookings
      if date_from <= b['start_datetime'].date() <= date_to
    ]

  return bookings

@anvil.server.callable
def update_booking_status(booking_id, new_status):
  """Update booking status"""
  booking = app_tables.tbl_bookings.get_by_id(booking_id)
  if booking:
    booking['status'] = new_status
    booking.update()
    return {'success': True}
  return {'success': False, 'error': 'Booking not found'}

@anvil.server.callable
def cancel_booking(booking_id, reason):
  """Cancel a booking"""
  booking = app_tables.tbl_bookings.get_by_id(booking_id)
  if booking:
    booking['status'] = 'cancelled'
    booking['notes'] = f"Cancelled: {reason}"
    booking.update()

    # TODO: Send cancellation email
    # TODO: Process refund if payment made

    return {'success': True}
  return {'success': False, 'error': 'Booking not found'}

*****

@anvil.server.callable
def search_booking_for_checkin(search_term):
  """Search for booking by number or guest name"""
  user = anvil.users.get_user()

  # Try booking number first
  booking = app_tables.tbl_bookings.get(
    client_id=user,
    booking_number=search_term
  )

  if booking:
    return booking

  # Try guest email
  bookings = list(app_tables.tbl_bookings.search(
    client_id=user
  ))

  for b in bookings:
    if b.get('customer_id') and search_term.lower() in b['customer_id']['email'].lower():
      return b

  return None

@anvil.server.callable
def process_check_in(booking_id, checkin_data):
  """Process guest check-in"""
  try:
    booking = app_tables.tbl_bookings.get_by_id(booking_id)

    if not booking:
      return {'success': False, 'error': 'Booking not found'}

    if booking['status'] != 'confirmed':
      return {'success': False, 'error': f'Cannot check in - status is {booking["status"]}'}

    # Update booking
    booking['status'] = 'checked_in'
    booking['checked_in_at'] = datetime.now()
    booking['id_document'] = checkin_data['id_document']
    booking['key_number'] = checkin_data.get('key_number', '')

    # Add notes
    if checkin_data.get('special_requests'):
      current_notes = booking.get('notes', '')
      booking['notes'] = f"{current_notes}\nCheck-in requests: {checkin_data['special_requests']}"

    booking.update()

    # TODO: Send welcome email

    return {'success': True}

  except Exception as e:
    print(f"Error processing check-in: {e}")
    return {'success': False, 'error': str(e)}

@anvil.server.callable
def process_check_out(booking_id, checkout_data):
  """Process guest check-out"""
  try:
    booking = app_tables.tbl_bookings.get_by_id(booking_id)

    if not booking:
      return {'success': False, 'error': 'Booking not found'}

    if booking['status'] != 'checked_in':
      return {'success': False, 'error': f'Cannot check out - status is {booking["status"]}'}

    # Update booking
    booking['status'] = 'checked_out'
    booking['checked_out_at'] = datetime.now()
    booking['final_amount'] = checkout_data['total']
    booking['payment_status'] = checkout_data['payment_status']

    # Add charges breakdown to notes
    notes = f"\nCheckout - Extras: ${checkout_data['extras']:.2f}, Tax: ${checkout_data['tax']:.2f}, Total: ${checkout_data['total']:.2f}"
    current_notes = booking.get('notes', '')
    booking['notes'] = current_notes + notes

    booking.update()

    # Update room status to 'dirty' (needs cleaning)
    if booking.get('resource_id'):
      booking['resource_id']['status'] = 'dirty'
      booking['resource_id'].update()

    # TODO: Send thank you email
    # TODO: Process payment if outstanding

    return {'success': True}

  except Exception as e:
    print(f"Error processing check-out: {e}")
    return {'success': False, 'error': str(e)}

*****

@anvil.server.callable
def get_customer(customer_id):
  """Get customer details"""
  customer = app_tables.users.get_by_id(customer_id)
  return customer

@anvil.server.callable
def get_client_notes(customer_id):
  """Get all notes for a customer"""
  user = anvil.users.get_user()
  customer = app_tables.users.get_by_id(customer_id)

  # Check user permissions
  if user['role'] not in ['owner', 'manager', 'staff']:
    return []

  # Get notes
  notes = list(app_tables.tbl_client_notes.search(
    customer_id=customer,
    tables.order_by('created_at', ascending=False)
  ))

  # Filter confidential notes if not manager/owner
  if user['role'] not in ['owner', 'manager']:
    notes = [n for n in notes if not n.get('is_confidential', False)]

  return notes

@anvil.server.callable
def add_client_note(note_data):
  """Add new client note"""
  try:
    user = anvil.users.get_user()

    # Check permissions
    if user['role'] not in ['owner', 'manager', 'staff']:
      return {'success': False, 'error': 'Insufficient permissions'}

    customer = app_tables.users.get_by_id(note_data['customer_id'])

    # Create note
    app_tables.tbl_client_notes.add_row(
      client_id=user,
      customer_id=customer,
      note=note_data['note'],
      is_confidential=note_data.get('is_confidential', False),
      created_by=user,
      created_at=datetime.now()
    )

    return {'success': True}

  except Exception as e:
    print(f"Error adding client note: {e}")
    return {'success': False, 'error': str(e)}


    *****

    @anvil.server.callable
    def get_public_guestbook_entries():
      """Get approved public guestbook entries"""
  # Get entries where is_approved = True and is_public = True
  entries = list(app_tables.tbl_guestbook_entries.search(
    is_approved=True,
    is_public=True,
    tables.order_by('created_at', ascending=False)
  ))

  return entries

@anvil.server.callable
def submit_guestbook_entry(entry_data):
  """Submit new guestbook entry"""
  try:
    # Add entry (requires approval)
    app_tables.tbl_guestbook_entries.add_row(
      guest_name=entry_data['guest_name'],
      guest_email=entry_data['guest_email'],
      rating=entry_data['rating'],
      comment=entry_data['comment'],
      is_approved=False,  # Requires admin approval
      is_public=False,    # Will be set to True when approved
      created_at=datetime.now()
    )

    # TODO: Send notification to admin for approval

    return {'success': True}

  except Exception as e:
    print(f"Error submitting guestbook entry: {e}")
    return {'success': False, 'error': str(e)}

*****

@anvil.server.callable
def get_public_bookable_resources():
  """Get resources available for public booking"""
  # Get resources where public_booking_enabled = True
  return list(app_tables.tbl_bookable_resources.search(
    is_active=True
  ))

@anvil.server.callable
def get_available_time_slots(resource_id, date):
  """Get available time slots for resource on date"""
  try:
    resource = app_tables.tbl_bookable_resources.get_by_id(resource_id)

    # Get availability hours for this day of week
    day_of_week = date.weekday()  # 0=Monday, 6=Sunday
    availability = app_tables.tbl_availability.get(
      resource_id=resource,
      day_of_week=day_of_week
    )

    if not availability or not availability['is_available']:
      return []

    # Generate hourly slots
    slots = []
    start_hour, start_min = map(int, availability['start_time'].split(':'))
    end_hour, end_min = map(int, availability['end_time'].split(':'))

    current_hour = start_hour
    while current_hour < end_hour:
      slot_time = f"{current_hour:02d}:00"

      # Check if slot is booked
      slot_datetime = datetime.combine(date, datetime.min.time()).replace(hour=current_hour)

      is_booked = len(list(app_tables.tbl_bookings.search(
        resource_id=resource,
        start_datetime=slot_datetime,
        status=q.any_of('pending', 'confirmed')
      ))) > 0

      if not is_booked:
        slots.append({
          'time': slot_time,
          'time_display': datetime.strptime(slot_time, '%H:%M').strftime('%I:%M %p')
        })

      current_hour += 1

    return slots

  except Exception as e:
    print(f"Error getting time slots: {e}")
    return []

@anvil.server.callable
def create_public_booking(booking_data):
  """Create booking from public widget"""
  try:
    # Get or create customer
    customer = app_tables.users.get(email=booking_data['customer_email'])

    if not customer:
      # Create guest customer
      customer = app_tables.users.add_row(
        email=booking_data['customer_email'],
        role='customer',
        account_status='active',
        created_at=datetime.now()
      )

    # Get resource
    resource = app_tables.tbl_bookable_resources.get_by_id(booking_data['resource_id'])

    # Calculate end time (default 1 hour)
    end_datetime = booking_data['start_datetime'] + timedelta(hours=1)

    # Create booking
    booking = app_tables.tbl_bookings.add_row(
      client_id=resource['client_id'],
      customer_id=customer,
      resource_id=resource,
      booking_type='appointment',
      start_datetime=booking_data['start_datetime'],
      end_datetime=end_datetime,
      status='pending',
      total_amount=0,
      customer_notes=booking_data.get('notes', ''),
      created_at=datetime.now(),
      booking_number=f"BK-{datetime.now().strftime('%Y%m%d')}-{len(list(app_tables.tbl_bookings.search()))+1:03d}"
    )

    # Send confirmation email
    # TODO: Implement in Phase 2

    return {'success': True, 'booking_id': booking.get_id()}

  except Exception as e:
    print(f"Error creating public booking: {e}")
    return {'success': False, 'error': str(e)}


    *****

    @anvil.server.callable
    def get_all_rooms():
      """Get all rooms"""
  user = anvil.users.get_user()
  return list(app_tables.tbl_rooms.search(
    client_id=user,
    tables.order_by('room_number')
  ))

@anvil.server.callable
def get_room(room_id):
  """Get single room"""
  user = anvil.users.get_user()
  room = app_tables.tbl_rooms.get_by_id(room_id)

  if room and room['client_id'] == user:
    return room
  return None

@anvil.server.callable
def save_room(room_id, room_data):
  """Save or update room"""
  try:
    user = anvil.users.get_user()

    if room_id:
      # Update existing
      room = app_tables.tbl_rooms.get_by_id(room_id)
      if room and room['client_id'] == user:
        room.update(**room_data)
    else:
      # Create new
      room_data['client_id'] = user
      app_tables.tbl_rooms.add_row(**room_data)

    return {'success': True}

  except Exception as e:
    print(f"Error saving room: {e}")
    return {'success': False, 'error': str(e)}

@anvil.server.callable
def delete_room(room_id):
  """Delete a room"""
  try:
    user = anvil.users.get_user()
    room = app_tables.tbl_rooms.get_by_id(room_id)

    if room and room['client_id'] == user:
      # Check if any active bookings exist
      active_bookings = len(list(
        app_tables.tbl_bookings.search(
          resource_id=room,
          status=q.any_of('pending', 'confirmed')
        )
      ))

      if active_bookings > 0:
        return {'success': False, 'error': f'{active_bookings} active bookings exist'}

      room.delete()
      return {'success': True}
    else:
      return {'success': False, 'error': 'Room not found'}

  except Exception as e:
    print(f"Error deleting room: {e}")
    return {'success': False, 'error': str(e)}

    *****

@anvil.server.callable
def get_rooms_with_status():
  """Get all rooms with current status and occupancy"""
  user = anvil.users.get_user()
  rooms = list(app_tables.tbl_rooms.search(
    client_id=user,
    tables.order_by('room_number')
  ))

  # Enhance with current status
  for room in rooms:
    # Determine display status
    if room['status'] == 'maintenance':
      room['display_status'] = 'maintenance'
    elif room['status'] == 'dirty':
      room['display_status'] = 'dirty'
    else:
      # Check if currently occupied
      current_booking = app_tables.tbl_bookings.get(
        resource_id=room,
        status='checked_in'
      )

      if current_booking:
        room['display_status'] = 'occupied'

        # Add guest info
        if current_booking.get('customer_id'):
          room['current_guest'] = current_booking['customer_id']['email'].split('@')[0]
        else:
          room['current_guest'] = 'Guest'

        room['checkout_date'] = current_booking['end_datetime'].strftime('%b %d')
        room['current_booking_id'] = current_booking.get_id()
      else:
        room['display_status'] = 'vacant'

  return rooms

@anvil.server.callable
def update_room_status(room_id, new_status):
  """Update room status"""
  try:
    room = app_tables.tbl_rooms.get_by_id(room_id)

    if room:
      room['status'] = new_status
      room.update()
      return {'success': True}
    else:
      return {'success': False, 'error': 'Room not found'}

  except Exception as e:
    print(f"Error updating room status: {e}")
    return {'success': False, 'error': str(e)}


*****

@anvil.server.callable
def get_all_services():
  """Get all services"""
  user = anvil.users.get_user()
  return list(app_tables.tbl_services.search(
    client_id=user,
    tables.order_by('service_name')
  ))

@anvil.server.callable
def get_service(service_id):
  """Get single service"""
  user = anvil.users.get_user()
  service = app_tables.tbl_services.get_by_id(service_id)

  if service and service['client_id'] == user:
    return service
  return None

@anvil.server.callable
def get_staff_members():
  """Get staff members for dropdown"""
  user = anvil.users.get_user()
  return list(app_tables.users.search(
    role=q.any_of('staff', 'manager', 'owner'),
    account_status='active'
  ))

@anvil.server.callable
def save_service(service_id, service_data):
  """Save or update service"""
  try:
    user = anvil.users.get_user()

    # Get staff member if provided
    if service_data.get('staff_id'):
      staff = app_tables.users.get_by_id(service_data['staff_id'])
      service_data['staff_id'] = staff
    else:
      service_data['staff_id'] = None

    if service_id:
      # Update existing
      service = app_tables.tbl_services.get_by_id(service_id)
      if service and service['client_id'] == user:
        service.update(**service_data)
    else:
      # Create new
      service_data['client_id'] = user
      app_tables.tbl_services.add_row(**service_data)

    return {'success': True}

  except Exception as e:
    print(f"Error saving service: {e}")
    return {'success': False, 'error': str(e)}

@anvil.server.callable
def delete_service(service_id):
  """Delete a service"""
  try:
    user = anvil.users.get_user()
    service = app_tables.tbl_services.get_by_id(service_id)

    if service and service['client_id'] == user:
      # Check if any active bookings use this service
      active_bookings = len(list(
        app_tables.tbl_bookings.search(
          service_id=service,
          status=q.any_of('pending', 'confirmed')
        )
      ))

      if active_bookings > 0:
        return {'success': False, 'error': f'{active_bookings} active bookings exist'}

      service.delete()
      return {'success': True}
    else:
      return {'success': False, 'error': 'Service not found'}

  except Exception as e:
    print(f"Error deleting service: {e}")
    return {'success': False, 'error': str(e)}


*****

@anvil.server.callable
def get_time_entries():
  """Get all time entries"""
  user = anvil.users.get_user()
  return list(app_tables.tbl_time_entries.search(
    client_id=user,
    tables.order_by('start_time', ascending=False)
  ))

@anvil.server.callable
def save_time_entry(entry_data):
  """Save time entry"""
  try:
    user = anvil.users.get_user()

    customer = app_tables.users.get_by_id(entry_data['customer_id'])
    service = app_tables.tbl_services.get_by_id(entry_data['service_id'])

    # Calculate billable amount
    hourly_rate = service['price'] / (service['duration_minutes'] / 60)
    hours = entry_data['duration_minutes'] / 60
    total_amount = hourly_rate * hours

    app_tables.tbl_time_entries.add_row(
      client_id=user,
      customer_id=customer,
      service_id=service,
      start_time=entry_data['start_time'],
      end_time=entry_data['end_time'],
      duration_minutes=entry_data['duration_minutes'],
      hourly_rate=hourly_rate,
      total_amount=total_amount,
      description=entry_data.get('description', ''),
      billable=True,
      invoiced=False,
      created_by=user,
      created_at=datetime.now()
    )

    return {'success': True}

  except Exception as e:
    print(f"Error saving time entry: {e}")
    return {'success': False, 'error': str(e)}

@anvil.server.callable
def delete_time_entry(entry_id):
  """Delete time entry"""
  entry = app_tables.tbl_time_entries.get_by_id(entry_id)
  if entry:
    entry.delete()
  return {'success': True}

  *****

@anvil.server.callable
def get_client_portal_data():
  """Get all client portal data"""
  try:
    user = anvil.users.get_user()

    # Upcoming appointments
    upcoming = list(app_tables.tbl_bookings.search(
      customer_id=user,
      status=q.any_of('pending', 'confirmed'),
      start_datetime=q.greater_than(datetime.now())
    ))

    upcoming_data = []
    for booking in upcoming:
      service_name = booking.get('service_id', {}).get('service_name', 'Appointment')
      staff_name = booking.get('staff_id', {}).get('email', 'Staff').split('@')[0]

      upcoming_data.append({
        'booking_id': booking.get_id(),
        'datetime': booking['start_datetime'],
        'service_name': service_name,
        'staff_name': staff_name
      })

    # Past appointments
    past = list(app_tables.tbl_bookings.search(
      customer_id=user,
      status=q.any_of('completed', 'cancelled'),
      tables.order_by('start_datetime', ascending=False)
    ))

    past_data = [{
      'datetime': b['start_datetime'],
      'service_name': b.get('service_id', {}).get('service_name', 'Appointment'),
      'status': b['status']
    } for b in past]

    # Invoices (placeholder)
    invoices = []

    # Documents (placeholder)
    documents = []

    return {
      'upcoming': upcoming_data,
      'past': past_data,
      'invoices': invoices,
      'documents': documents
    }

  except Exception as e:
    print(f"Error getting portal data: {e}")
    return {
      'upcoming': [],
      'past': [],
      'invoices': [],
      'documents': []
    }

*****

@anvil.server.callable
def get_guest_history(guest_id):
  """Get complete guest history"""
  try:
    guest = app_tables.users.get_by_id(guest_id)

    if not guest:
      return None

    # Get all bookings
    bookings = list(app_tables.tbl_bookings.search(
      customer_id=guest,
      tables.order_by('start_datetime', ascending=False)
    ))

    # Calculate stats
    total_stays = len([b for b in bookings if b['status'] in ['completed', 'checked_in']])

    total_nights = 0
    for booking in bookings:
      if booking['status'] in ['completed', 'checked_in']:
        nights = (booking['end_datetime'].date() - booking['start_datetime'].date()).days
        total_nights += nights

    total_revenue = sum(b.get('total_amount', 0) for b in bookings if b['status'] == 'completed')

    last_visit = None
    if bookings:
      last_visit = bookings[0]['start_datetime']

    # Find favorite room
    room_counts = {}
    for booking in bookings:
      if booking.get('resource_id'):
        room_name = booking['resource_id']['room_number']
        room_counts[room_name] = room_counts.get(room_name, 0) + 1

    favorite_room = max(room_counts.items(), key=lambda x: x[1])[0] if room_counts else 'None'

    # Format booking data
    booking_data = []
    for booking in bookings:
      nights = (booking['end_datetime'].date() - booking['start_datetime'].date()).days
      room_name = booking['resource_id']['room_number'] if booking.get('resource_id') else 'Unknown'

      booking_data.append({
        'start_date': booking['start_datetime'],
        'end_date': booking['end_datetime'],
        'nights': nights,
        'room_name': room_name,
        'amount': booking.get('total_amount', 0),
        'status': booking['status']
      })

    # Get notes
    notes = list(app_tables.tbl_client_notes.search(
      customer_id=guest,
      tables.order_by('created_at', ascending=False)
    ))

    note_data = [{'note': n['note']} for n in notes]

    return {
      'guest': guest,
      'stats': {
        'total_stays': total_stays,
        'total_nights': total_nights,
        'total_revenue': total_revenue,
        'last_visit': last_visit,
        'favorite_room': favorite_room
      },
      'bookings': booking_data,
      'notes': note_data
    }

  except Exception as e:
    print(f"Error getting guest history: {e}")
    return None

@anvil.server.callable
def add_guest_note(guest_id, note_text):
  """Add note to guest profile"""
  user = anvil.users.get_user()
  guest = app_tables.users.get_by_id(guest_id)

  app_tables.tbl_client_notes.add_row(
    client_id=user,
    customer_id=guest,
    note=note_text,
    is_confidential=False,
    created_by=user,
    created_at=datetime.now()
  )

  return {'success': True}


*****

@anvil.server.callable
def get_my_tickets(status_filter='all'):
  """Get current user's tickets"""
  user = anvil.users.get_user()

  query = {'customer_id': user}

  if status_filter != 'all':
    query['status'] = status_filter

  tickets = list(app_tables.tbl_tickets.search(
    tables.order_by('created_at', ascending=False),
    **query
  ))

  return tickets

@anvil.server.callable
def create_ticket(ticket_data):
  """Create new support ticket"""
  try:
    user = anvil.users.get_user()

    # Generate ticket number
    count = len(list(app_tables.tbl_tickets.search()))
    ticket_number = f"TKT-{datetime.now().strftime('%Y%m%d')}-{count+1:03d}"

    # Create ticket
    ticket = app_tables.tbl_tickets.add_row(
      ticket_number=ticket_number,
      customer_id=user,
      customer_email=user['email'],
      subject=ticket_data['subject'],
      description=ticket_data['description'],
      category=ticket_data['category'],
      priority=ticket_data['priority'],
      status='open',
      created_at=datetime.now(),
      updated_at=datetime.now()
    )

    # Add initial message
    app_tables.tbl_ticket_messages.add_row(
      ticket_id=ticket,
      author_id=user,
      author_type='customer',
      message=ticket_data['description'],
      is_internal_note=False,
      created_at=datetime.now()
    )

    # TODO: Send confirmation email

    return {'success': True, 'ticket_id': ticket.get_id()}

  except Exception as e:
    print(f"Error creating ticket: {e}")
    return {'success': False, 'error': str(e)}

@anvil.server.callable
def get_ticket_messages(ticket_id):
  """Get all messages for a ticket"""
  ticket = app_tables.tbl_tickets.get_by_id(ticket_id)

  messages = list(app_tables.tbl_ticket_messages.search(
    ticket_id=ticket,
    tables.order_by('created_at')
  ))

  # Add author name
  for msg in messages:
    if msg.get('author_id'):
      msg['author_name'] = msg['author_id']['email'].split('@')[0]
    else:
      msg['author_name'] = 'Support'

  return messages

@anvil.server.callable
def add_ticket_message(ticket_id, message_text):
  """Add message to ticket"""
  try:
    user = anvil.users.get_user()
    ticket = app_tables.tbl_tickets.get_by_id(ticket_id)

    app_tables.tbl_ticket_messages.add_row(
      ticket_id=ticket,
      author_id=user,
      author_type='customer',
      message=message_text,
      is_internal_note=False,
      created_at=datetime.now()
    )

    # Update ticket
    ticket['updated_at'] = datetime.now()
    ticket.update()

    # TODO: Notify support staff

    return {'success': True}

  except Exception as e:
    print(f"Error adding message: {e}")
    return {'success': False, 'error': str(e)}

*****

@anvil.server.callable
def get_all_customers_filtered(filters):
  """Get all customers with filters"""
  user = anvil.users.get_user()

  query = {}

  # Role filter
  if filters.get('role'):
    query['role'] = filters['role']

  # Status filter
  if filters.get('status'):
    query['account_status'] = filters['status']

  # Get customers
  customers = list(app_tables.users.search(
    tables.order_by('created_at', ascending=False),
    **query
  ))

  # Search filter (client-side for simplicity)
  if filters.get('search'):
    search_term = filters['search'].lower()
    customers = [
      c for c in customers
      if search_term in c['email'].lower()
    ]

  return customers

@anvil.server.callable
def save_customer(customer_id, customer_data):
  """Save or update customer"""
  try:
    if customer_id:
      # Update existing
      customer = app_tables.users.get_by_id(customer_id)
      if customer:
        customer.update(**customer_data)
    else:
      # Create new
      customer_data['created_at'] = datetime.now()
      # TODO: Send welcome email with password setup link
      app_tables.users.add_row(**customer_data)

    return {'success': True}

  except Exception as e:
    print(f"Error saving customer: {e}")
    return {'success': False, 'error': str(e)}


*****

@anvil.server.callable
def get_customer_details(customer_id):
  """Get customer with activity summary"""
  try:
    customer = app_tables.users.get_by_id(customer_id)

    if not customer:
      return None

    # Calculate summary
    orders = list(app_tables.tbl_orders.search(customer_id=customer))
    bookings = list(app_tables.tbl_bookings.search(customer_id=customer))
    tickets = list(app_tables.tbl_tickets.search(customer_id=customer))
    reviews = list(app_tables.tbl_reviews.search(customer_id=customer))

    total_spent = sum(o.get('total_amount', 0) for o in orders)

    return {
      'customer': customer,
      'summary': {
        'orders_count': len(orders),
        'total_spent': total_spent,
        'bookings_count': len(bookings),
        'tickets_count': len(tickets),
        'reviews_count': len(reviews)
      }
    }

  except Exception as e:
    print(f"Error getting customer details: {e}")
    return None

@anvil.server.callable
def get_customer_orders(customer_id):
  """Get customer's orders"""
  customer = app_tables.users.get_by_id(customer_id)
  orders = list(app_tables.tbl_orders.search(
    customer_id=customer,
    tables.order_by('created_at', ascending=False)
  ))

  return [{
    'number': o['order_number'],
    'date': o['created_at'],
    'amount': o['total_amount'],
    'status': o['status']
  } for o in orders[:10]]

@anvil.server.callable
def get_customer_bookings(customer_id):
  """Get customer's bookings"""
  customer = app_tables.users.get_by_id(customer_id)
  bookings = list(app_tables.tbl_bookings.search(
    customer_id=customer,
    tables.order_by('start_datetime', ascending=False)
  ))

  return [{
    'number': b['booking_number'],
    'date': b['start_datetime'],
    'amount': b.get('total_amount', 0),
    'status': b['status']
  } for b in bookings[:10]]

@anvil.server.callable
def get_customer_tickets(customer_id):
  """Get customer's support tickets"""
  customer = app_tables.users.get_by_id(customer_id)
  tickets = list(app_tables.tbl_tickets.search(
    customer_id=customer,
    tables.order_by('created_at', ascending=False)
  ))

  return [{
    'number': t['ticket_number'],
    'date': t['created_at'],
    'amount': None,
    'status': t['status']
  } for t in tickets[:10]]

@anvil.server.callable
def get_customer_reviews(customer_id):
  """Get customer's reviews"""
  customer = app_tables.users.get_by_id(customer_id)
  reviews = list(app_tables.tbl_reviews.search(
    customer_id=customer,
    tables.order_by('created_at', ascending=False)
  ))

  return [{
    'number': f"⭐ {r.get('rating', 0)}/5",
    'date': r['created_at'],
    'amount': None,
    'status': r.get('status', 'pending')
  } for r in reviews[:10]]

  *****

  