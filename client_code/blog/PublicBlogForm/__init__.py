from ._anvil_designer import BlogEditorFormTemplate
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

class PublicBlogForm(PublicBlogFormTemplate):
  def __init__(self, **properties):
    self.selected_category = None
    self.init_components(**properties)

    # Configure back link
    self.link_back.text = "← Back to Home"
    self.link_back.role = "secondary-color"

    # Configure search box
    self.txt_search.placeholder = "Search posts..."
    self.txt_search.icon = "fa:search"

    # Configure sidebar title
    self.lbl_categories_title.text = "CATEGORIES"
    self.lbl_categories_title.bold = True
    self.lbl_categories_title.font_size = 14
    self.lbl_categories_title.foreground = "#666666"

    # Configure main title
    self.lbl_title.text = "Our Blog"
    self.lbl_title.font_size = 28
    self.lbl_title.bold = True
    self.lbl_title.role = "headline"

    # Configure repeating panels
    self.rp_categories.item_template = 'blog.PublicCategoryTemplate'
    self.rp_posts.item_template = 'blog.PublicPostCardTemplate'

    # Configure no posts label
    self.lbl_no_posts.text = "No blog posts published yet. Check back soon!"
    self.lbl_no_posts.align = "center"
    self.lbl_no_posts.foreground = "#666666"
    self.lbl_no_posts.visible = False

    # Load data
    self.load_categories()
    self.load_posts()

  def load_categories(self):
    """Load category filter sidebar"""
    try:
      categories = anvil.server.call('get_public_blog_categories')

      # Add "All Posts" option
      all_option = {'name': 'All Posts', 'id': None, 'is_all': True}
      self.rp_categories.items = [all_option] + list(categories)

    except Exception as e:
      print(f"Error loading categories: {e}")

  def load_posts(self, **event_args):
    """Load published blog posts"""
    try:
      search_term = self.txt_search.text or None

      posts = anvil.server.call(
        'get_public_blog_posts',
        self.selected_category,
        search_term
      )

      if posts:
        self.rp_posts.items = posts
        self.rp_posts.visible = True
        self.lbl_no_posts.visible = False
      else:
        self.rp_posts.visible = False
        self.lbl_no_posts.visible = True

    except Exception as e:
      alert(f"Error loading posts: {str(e)}")

  @handle("link_back", "click")
  def link_back_click(self, **event_args):
    """Navigate back to home"""
    open_form('HomePage')  # Or whatever your home form is

  def textbox_search_pressed_enter(self, **event_args):
    """Search on Enter key"""
    self.load_posts()

  def filter_by_category(self, category_id):
    """Called by category row template"""
    self.selected_category = category_id
    self.load_posts()

  @handle("txt_search", "pressed_enter")
  def txt_search_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    pass
