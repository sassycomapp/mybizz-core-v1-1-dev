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

    