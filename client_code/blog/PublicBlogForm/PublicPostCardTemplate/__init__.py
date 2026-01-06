from ._anvil_designer import PublicPostCardTemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class PublicPostCardTemplate(PublicPostCardTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    # Configure featured image
    if self.item.get('featured_image'):
      self.img_featured.source = self.item['featured_image']
      self.img_featured.height = 200
    else:
      self.img_featured.visible = False

    # Configure title
    self.lbl_title.text = self.item['title']
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True

    # Configure excerpt
    excerpt = self.item.get('excerpt', '')
    if not excerpt and self.item.get('content'):
      # Generate excerpt from content (first 150 chars)
      excerpt = self.item['content'][:150] + "..."
    self.lbl_excerpt.text = excerpt
    self.lbl_excerpt.foreground = "#666666"

    # Configure meta info
    category = self.item.get('category_name', 'Uncategorized')
    date = self.item['published_at'].strftime('%b %d, %Y')
    self.lbl_meta.text = f"{category} • {date}"
    self.lbl_meta.font_size = 12
    self.lbl_meta.foreground = "#999999"

    # Configure read more link
    self.link_read_more.text = "Read More →"
    self.link_read_more.role = "primary-color"

  @handle("link_read_more", "click")
  def link_read_more_click(self, **event_args):
    """Navigate to full post"""
    open_form('blog.BlogPostDetailForm', slug=self.item['slug'])