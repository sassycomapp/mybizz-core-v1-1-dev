from ._anvil_designer import KBArticleDetailFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class KBArticleDetailForm(KBArticleDetailFormTemplate):
  """Knowledge base article detail view"""

  def __init__(self, slug=None, **properties):
    self.slug = slug
    self.article = None
    self.init_components(**properties)

    # Load article
    if slug:
      self.load_article()

  def load_article(self):
    """Load article by slug"""
    try:
      result = anvil.server.call('get_article_by_slug', self.slug)

      if result['success']:
        self.article = result['data']['article']
        related = result['data']['related_articles']

        # Breadcrumb
        category = self.article['category_id']['name']
        self.lbl_breadcrumb.text = f"Help Center > {category} > {self.article['title']}"
        self.lbl_breadcrumb.foreground = "#666666"
        self.lbl_breadcrumb.font_size = 12

        # Title
        self.lbl_title.text = self.article['title']
        self.lbl_title.font_size = 28
        self.lbl_title.bold = True

        # Content
        self.rt_content.content = self.article['content']
        self.rt_content.enable_slots = False

        # Helpful question
        self.lbl_helpful_question.text = "Was this helpful?"
        self.lbl_helpful_question.font_size = 16
        self.lbl_helpful_question.bold = True

        # Helpful buttons
        helpful_count = self.article.get('helpful_count', 0)
        unhelpful_count = self.article.get('unhelpful_count', 0)

        self.btn_helpful_yes.text = f"👍 Yes ({helpful_count})"
        self.btn_helpful_yes.role = "outlined-button"

        self.btn_helpful_no.text = f"👎 No ({unhelpful_count})"
        self.btn_helpful_no.role = "outlined-button"

        # Related articles
        self.lbl_related.text = "Related Articles:"
        self.lbl_related.font_size = 16
        self.lbl_related.bold = True

        self.rp_related.items = related

      else:
        alert(f"Article not found: {self.slug}")

    except Exception as e:
      print(f"Error loading article: {e}")
      alert(f"Failed to load article: {str(e)}")

  def button_helpful_yes_click(self, **event_args):
    """Mark article as helpful"""
    try:
      result = anvil.server.call('mark_article_helpful', self.article.get_id(), True)

      if result['success']:
        Notification("Thank you for your feedback!", style="success").show()

        # Update count
        helpful_count = self.article.get('helpful_count', 0) + 1
        self.article['helpful_count'] = helpful_count
        self.btn_helpful_yes.text = f"👍 Yes ({helpful_count})"

    except Exception as e:
      print(f"Error: {e}")

  def button_helpful_no_click(self, **event_args):
    """Mark article as not helpful"""
    try:
      result = anvil.server.call('mark_article_helpful', self.article.get_id(), False)

      if result['success']:
        Notification("Thank you for your feedback!", style="info").show()

        # Update count
        unhelpful_count = self.article.get('unhelpful_count', 0) + 1
        self.article['unhelpful_count'] = unhelpful_count
        self.btn_helpful_no.text = f"👎 No ({unhelpful_count})"

    except Exception as e:
      print(f"Error: {e}")

  @handle("btn_helpful_yes", "click")
  def btn_helpful_yes_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_helpful_no", "click")
  def btn_helpful_no_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
