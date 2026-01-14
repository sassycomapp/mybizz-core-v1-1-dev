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
def get_page_by_slug(slug):
  """
  Get published page by slug for public display.
  
  Args:
    slug (str): Page slug
    
  Returns:
    dict: {'success': bool, 'data': row} or {'success': bool, 'error': str}
  """
  try:
    # Get published page only
    page = app_tables.pages.get(slug=slug, is_published=True)

    if not page:
      return {'success': False, 'error': 'Page not found or not published'}

    # Increment view count (optional analytics)
    page['view_count'] = page.get('view_count', 0) + 1
    page.update()

    return {'success': True, 'data': page}

  except Exception as e:
    print(f"Error getting page: {e}")
    return {'success': False, 'error': str(e)}


import anvil.server
import anvil.users
from anvil.tables import app_tables
import anvil.tables as tables

@anvil.server.callable
@anvil.users.login_required
def get_all_pages():
  """
  Get all pages for editing.
  
  Returns:
    dict: {'success': bool, 'data': list} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    pages = list(app_tables.pages.search(
      tables.order_by('name')
    ))

    return {'success': True, 'data': pages}

  except Exception as e:
    print(f"Error getting pages: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
@anvil.users.login_required
def create_page(name):
  """
  Create new page.
  
  Args:
    name (str): Page name
    
  Returns:
    dict: {'success': bool, 'data': row} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    # Generate slug from name
    slug = name.lower().replace(' ', '-').replace('/', '-')

    # Check if slug exists
    existing = app_tables.pages.get(slug=slug)
    if existing:
      return {'success': False, 'error': 'Page with this name already exists'}

    # Create page
    page = app_tables.pages.add_row(
      name=name,
      slug=slug,
      components=[],
      is_published=False,
      created_at=datetime.now(),
      updated_at=datetime.now()
    )

    return {'success': True, 'data': page}

  except Exception as e:
    print(f"Error creating page: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
@anvil.users.login_required
def save_page(page_id, components, is_published):
  """
  Save page components and publish status.
  
  Args:
    page_id (str): Page ID
    components (list): List of component dictionaries
    is_published (bool): Publish status
    
  Returns:
    dict: {'success': bool} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    page = app_tables.pages.get_by_id(page_id)

    if not page:
      return {'success': False, 'error': 'Page not found'}

    # Update page
    page['components'] = components
    page['is_published'] = is_published
    page['updated_at'] = datetime.now()
    page.update()

    return {'success': True}

  except Exception as e:
    print(f"Error saving page: {e}")
    return {'success': False, 'error': str(e)}