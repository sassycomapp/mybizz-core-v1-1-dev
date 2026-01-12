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
def get_product_by_slug(slug):
  """
  Get product by URL slug.
  
  Args:
    slug (str): Product slug
    
  Returns:
    dict: {'success': bool, 'data': product} or {'success': bool, 'error': str}
  """
  try:
    product = app_tables.products.get(slug=slug, is_active=True)

    if not product:
      return {'success': False, 'error': 'Product not found'}

    return {'success': True, 'data': product}

  except Exception as e:
    print(f"Error getting product by slug: {e}")
    return {'success': False, 'error': str(e)}