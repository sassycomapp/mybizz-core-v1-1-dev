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

    