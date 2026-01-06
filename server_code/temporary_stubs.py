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

