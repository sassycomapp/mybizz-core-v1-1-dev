from ._anvil_designer import RelatedArticleTemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class RelatedArticleTemplate(RelatedArticleTemplateTemplate):
  """Related article link"""

  def __init__(self, **properties):
    self.article = self.item
    self.init_components(**properties)

    # Configure link
    self.link_article.text = f"• {self.article['title']}"
    self.link_article.url = f"/help/{self.article['slug']}"
    self.link_article.foreground = "#2196F3"
    self.link_article.font_size = 14