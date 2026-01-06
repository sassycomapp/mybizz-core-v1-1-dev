from ._anvil_designer import CategoryRowTemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class CategoryRowTemplate(CategoryRowTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    # Display category data
    self.lbl_name.text = self.item['name']
    self.lbl_name.bold = True

    self.lbl_slug.text = self.item['slug']
    self.lbl_slug.foreground = "#666666"

    # Configure action links
    self.link_edit.text = "✏️ Edit"
    self.link_edit.role = "secondary-color"

    self.link_delete.text = "🗑️ Delete"
    self.link_delete.role = "danger"

  @handle("link_edit", "click")
  def link_edit_click(self, **event_args):
    """Edit this category"""
    result = alert(
      content=CategoryEditorModal(category_id=self.item.get_id()),
      title="Edit Category",
      large=False,
      buttons=[("Cancel", False), ("Save", True)]
    )

    if result:
      self.parent.raise_event('x-refresh-categories')

  @handle("link_delete", "click")
  def link_delete_click(self, **event_args):
    """Delete this category"""
    if confirm(f"Delete category '{self.item['name']}'?"):
      try:
        anvil.server.call('delete_blog_category', self.item.get_id())
        Notification("Category deleted successfully").show()
        self.parent.raise_event('x-refresh-categories')
      except Exception as e:
        alert(f"Error deleting category: {str(e)}")