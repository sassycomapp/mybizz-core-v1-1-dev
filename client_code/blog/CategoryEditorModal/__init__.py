from ._anvil_designer import CategoryEditorModalTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


import re

class CategoryEditorModal(CategoryEditorModalTemplate):
  def __init__(self, category_id=None, **properties):
    self.category_id = category_id
    self.init_components(**properties)

    # Configure labels
    self.lbl_name_field.text = "Category Name *"
    self.lbl_name_field.bold = True

    self.lbl_description_field.text = "Description (optional)"
    self.lbl_description_field.bold = True

    # Configure name field
    self.txt_name.placeholder = "Enter category name..."

    # Configure description field
    self.txt_description.placeholder = "Optional description..."
    self.txt_description.rows = 3

    # Load existing category if editing
    if self.category_id:
      self.load_category()

  def load_category(self):
    """Load existing category"""
    try:
      category = anvil.server.call('get_blog_category', self.category_id)
      if category:
        self.txt_name.text = category['name']
        self.txt_description.text = category.get('description', '')
    except Exception as e:
      alert(f"Error loading category: {str(e)}")

  def save(self):
    """Save category (called when user clicks Save button)"""
    try:
      if not self.txt_name.text:
        alert("Category name is required")
        return False

      # Generate slug from name
      slug = self.generate_slug(self.txt_name.text)

      category_data = {
        'name': self.txt_name.text,
        'slug': slug,
        'description': self.txt_description.text
      }

      result = anvil.server.call(
        'save_blog_category',
        self.category_id,
        category_data
      )

      if result['success']:
        return True
      else:
        alert(result['error'])
        return False

    except Exception as e:
      alert(f"Error saving category: {str(e)}")
      return False

  def generate_slug(self, name):
    """Convert name to URL slug"""
    slug = name.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')