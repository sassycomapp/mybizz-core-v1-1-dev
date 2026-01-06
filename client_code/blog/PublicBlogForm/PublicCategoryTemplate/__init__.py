from ._anvil_designer import PublicCategoryTemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class PublicCategoryTemplate(PublicCategoryTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    # Configure checkbox as radio button style
    self.cb_category.text = self.item['name']
    self.cb_category.checked = self.item.get('is_all', False)

  def checkbox_category_change(self, **event_args):
    """Filter posts by this category"""
    if self.cb_category.checked:
      # Uncheck other categories (radio button behavior)
      for row in self.parent.get_components():
        if row != self:
          row.cb_category.checked = False

      # Filter posts
      category_id = None if self.item.get('is_all') else self.item.get_id()
      self.parent.parent.filter_by_category(category_id)
