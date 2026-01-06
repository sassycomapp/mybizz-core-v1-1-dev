from ._anvil_designer import CategoryManagementFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import re  # ← Only add this for slug generation

class CategoryManagementForm(CategoryManagementFormTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "Manage Blog Categories"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True
    self.lbl_title.role = "headline"

    # Configure new button
    self.btn_new_category.text = "New Category"
    self.btn_new_category.icon = "fa:plus"
    self.btn_new_category.role = "primary-color"

    # Configure no categories label
    self.lbl_no_categories.text = "No categories yet. Click 'New Category' to create one!"
    self.lbl_no_categories.align = "center"
    self.lbl_no_categories.foreground = "#666666"
    self.lbl_no_categories.visible = False

    # Set repeating panel template
    self.rp_categories.item_template = 'blog.CategoryRowTemplate'

    # Load categories
    self.load_categories()

  def load_categories(self, **event_args):
    """Load all categories"""
    try:
      categories = anvil.server.call('get_blog_categories')

      if categories:
        self.rp_categories.items = categories
        self.rp_categories.visible = True
        self.lbl_no_categories.visible = False
      else:
        self.rp_categories.visible = False
        self.lbl_no_categories.visible = True

    except Exception as e:
      alert(f"Error loading categories: {str(e)}")

  def button_new_category_click(self, **event_args):
    """Open category editor"""
    result = alert(
      content=CategoryEditorModal(category_id=None),
      title="Add New Category",
      large=False,
      buttons=[("Cancel", False), ("Save", True)]
    )

    if result:
      self.load_categories()

  @handle("btn_new_category", "click")
  def btn_new_category_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
