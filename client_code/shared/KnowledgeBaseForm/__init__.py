from ._anvil_designer import KnowledgeBaseFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class KnowledgeBaseForm(KnowledgeBaseFormTemplate):
  """Public knowledge base / help center"""

  def __init__(self, **properties):
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "Help Center"
    self.lbl_title.font_size = 28
    self.lbl_title.bold = True

    # Configure search box
    self.txt_search.placeholder = "🔍 Search help articles..."
    self.txt_search.font_size = 16

    # Configure section labels
    self.lbl_categories.text = "Browse by Category:"
    self.lbl_categories.font_size = 18
    self.lbl_categories.bold = True

    self.lbl_popular.text = "Popular Articles:"
    self.lbl_popular.font_size = 18
    self.lbl_popular.bold = True

    self.lbl_recent.text = "Recent Articles:"
    self.lbl_recent.font_size = 18
    self.lbl_recent.bold = True

    # Load content
    self.load_categories()
    self.load_popular_articles()
    self.load_recent_articles()

  def load_categories(self):
    """Load KB categories"""
    try:
      result = anvil.server.call('get_kb_categories')

      if result['success']:
        categories = result['data']

        # Clear flow panel
        self.flow_categories.clear()

        # Add category cards
        for category in categories:
          card = CategoryCardTemplate(item=category)
          self.flow_categories.add_component(card)

      else:
        print(f"Error loading categories: {result.get('error')}")

    except Exception as e:
      print(f"Error loading categories: {e}")

  def load_popular_articles(self):
    """Load popular articles"""
    try:
      result = anvil.server.call('get_popular_articles', limit=5)

      if result['success']:
        articles = result['data']
        self.rp_popular.items = articles
      else:
        print(f"Error loading popular articles: {result.get('error')}")

    except Exception as e:
      print(f"Error loading popular articles: {e}")

  def load_recent_articles(self):
    """Load recent articles"""
    try:
      result = anvil.server.call('get_recent_articles', limit=5)

      if result['success']:
        articles = result['data']
        self.rp_recent.items = articles
      else:
        print(f"Error loading recent articles: {result.get('error')}")

    except Exception as e:
      print(f"Error loading recent articles: {e}")

  def txt_search_pressed_enter(self, **event_args):
    """Search on Enter key"""
    self.search_articles()

  def search_articles(self):
    """Search knowledge base"""
    query = self.txt_search.text.strip()

    if not query:
      return

    try:
      result = anvil.server.call('search_kb_articles', query)

      if result['success']:
        articles = result['data']

        if articles:
          # Show search results
          self.show_search_results(articles)
        else:
          Notification("No articles found", style="info").show()
      else:
        alert(f"Search error: {result.get('error')}")

    except Exception as e:
      print(f"Search error: {e}")
      alert(f"Search failed: {str(e)}")

  def show_search_results(self, articles):
    """Display search results"""
    # Hide category browsing
    self.lbl_categories.visible = False
    self.flow_categories.visible = False
    self.lbl_popular.visible = False
    self.rp_popular.visible = False
    self.lbl_recent.visible = False
    self.rp_recent.visible = False

    # Show results
    self.lbl_categories.text = f"Search Results ({len(articles)} found):"
    self.lbl_categories.visible = True
    self.rp_popular.items = articles
    self.rp_popular.visible = True