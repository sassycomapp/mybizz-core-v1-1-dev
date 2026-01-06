from ._anvil_designer import BlogPostRowTemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class BlogPostRowTemplate(BlogPostRowTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    # Display data
    self.lbl_title.text = self.item['title']
    self.lbl_category.text = self.item.get('category_name', 'Uncategorized')
    self.lbl_status.text = self.item['status'].capitalize()

    # Color-code status
    if self.item['status'] == 'published':
      self.lbl_status.foreground = "green"
    else:
      self.lbl_status.foreground = "orange"

    # Format date
    if self.item.get('published_at'):
      self.lbl_date.text = self.item['published_at'].strftime('%b %d, %Y')
    else:
      self.lbl_date.text = "Not published"

  def link_edit_click(self, **event_args):
    """Edit this post"""
    open_form('blog.BlogEditorForm', post_id=self.item.get_id())

  def link_delete_click(self, **event_args):
    """Delete this post"""
    if confirm(f"Delete '{self.item['title']}'?"):
      try:
        anvil.server.call('delete_blog_post', self.item.get_id())
        Notification("Post deleted successfully").show()
        self.parent.raise_event('x-refresh-posts')
      except Exception as e:
        alert(f"Error deleting post: {str(e)}")