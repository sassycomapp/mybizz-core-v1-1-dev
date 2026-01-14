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
def create_kb_article(article_data):
  """Create new KB article"""
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    # Check slug uniqueness
    existing = app_tables.kb_articles.get(slug=article_data['slug'])
    if existing:
      return {'success': False, 'error': 'Slug already exists'}

    article = app_tables.kb_articles.add_row(
      title=article_data['title'],
      slug=article_data['slug'],
      category_id=app_tables.kb_categories.get_by_id(article_data['category_id']),
      excerpt=article_data.get('excerpt'),
      content=article_data['content'],
      keywords=article_data.get('keywords', []),
      published=article_data['published'],
      view_count=0,
      helpful_count=0,
      created_at=datetime.now(),
      updated_at=datetime.now()
    )

    return {'success': True, 'article_id': article.get_id()}

  except Exception as e:
    return {'success': False, 'error': str(e)}