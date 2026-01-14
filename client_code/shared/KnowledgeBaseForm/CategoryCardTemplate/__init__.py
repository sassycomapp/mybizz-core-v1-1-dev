from ._anvil_designer import CategoryCardTemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class CategoryCardTemplate(CategoryCardTemplateTemplate):
  """Category card with clickable link"""

  def __init__(self, **properties):
    self.category = self.item
    self.init_components(**properties)

    # Configure link (makes entire card clickable)
    self.link_category.url = None  # We'll handle navigation programmatically
    self.link_category.role = "card"

    # Icon
    icon = self.category.get('icon', '📄')
    self.lbl_icon.text = icon
    self.lbl_icon.font_size = 36
    self.lbl_icon.align = "center"

    # Name
    self.lbl_name.text = self.category['name']
    self.lbl_name.font_size = 14
    self.lbl_name.bold = True
    self.lbl_name.align = "center"

  def link_category_click(self, **event_args):
    """Navigate to category"""
    # Open category detail form
    from .KBCategoryForm import KBCategoryForm
    open_form('shared.KBCategoryForm', category_id=self.category.get_id())