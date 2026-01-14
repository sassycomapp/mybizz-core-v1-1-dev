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

@anvil.server.callable
def get_kb_categories():
  """
  Get all KB categories.
  
  Returns:
    dict: {'success': bool, 'data': list} or {'success': bool, 'error': str}
  """
  try:
    categories = list(app_tables.kb_categories.search(
      tables.order_by('sort_order')
    ))

    return {'success': True, 'data': categories}

  except Exception as e:
    print(f"Error getting KB categories: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
def get_popular_articles(limit=5):
  """
  Get most viewed articles.
  
  Args:
    limit (int): Maximum number of articles to return
    
  Returns:
    dict: {'success': bool, 'data': list} or {'success': bool, 'error': str}
  """
  try:
    articles = list(app_tables.kb_articles.search(
      published=True,
      tables.order_by('view_count', ascending=False)
    ))

    return {'success': True, 'data': articles[:limit]}

  except Exception as e:
    print(f"Error getting popular articles: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
def get_recent_articles(limit=5):
  """
  Get recently published articles.
  
  Args:
    limit (int): Maximum number of articles to return
    
  Returns:
    dict: {'success': bool, 'data': list} or {'success': bool, 'error': str}
  """
  try:
    articles = list(app_tables.kb_articles.search(
      published=True,
      tables.order_by('created_at', ascending=False)
    ))

    return {'success': True, 'data': articles[:limit]}

  except Exception as e:
    print(f"Error getting recent articles: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
def search_kb_articles(query):
  """
  Search KB articles by keyword.
  
  Args:
    query (str): Search query
    
  Returns:
    dict: {'success': bool, 'data': list} or {'success': bool, 'error': str}
  """
  try:
    query_lower = query.lower()
    articles = list(app_tables.kb_articles.search(published=True))

    # Filter articles by query in title, content, or keywords
    results = [
      a for a in articles
      if query_lower in a['title'].lower() or
      query_lower in a.get('content', '').lower() or
      any(query_lower in kw.lower() for kw in a.get('keywords', []))
    ]

    # Sort by relevance (title matches first)
    results.sort(key=lambda a: (
      query_lower not in a['title'].lower(),  # Title matches first (False < True)
      -a.get('view_count', 0)  # Then by popularity
    ))

    return {'success': True, 'data': results}

  except Exception as e:
    print(f"Error searching KB articles: {e}")
    return {'success': False, 'error': str(e)}