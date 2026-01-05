from ._anvil_designer import BlogListFormTemplate
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

class BlogListForm(BlogListFormTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "My Blog Posts"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True
    self.lbl_title.role = "headline"

    # Configure new post button
    self.btn_new_post.text = "New Post"
    self.btn_new_post.icon = "fa:plus"
    self.btn_new_post.role = "primary-color"

    # Configure status filter dropdown
    self.dd_status_filter.items = [
      ('All Posts', 'all'),
      ('Published', 'published'),
      ('Draft', 'draft')
    ]
    self.dd_status_filter.selected_value = 'all'
    self.dd_status_filter.placeholder = "Filter by status"

    # Configure search box
    self.txt_search.placeholder = "Search posts..."
    self.txt_search.icon = "fa:search"

    # Configure search button
    self.btn_search.text = ""
    self.btn_search.icon = "fa:search"
    self.btn_search.role = "secondary-color"

    # Configure data grid
    self.dg_posts.columns = [
      {'id': 'title', 'title': 'Title', 'data_key': 'title', 'width': 250},
      {'id': 'category', 'title': 'Category', 'data_key': 'category_name', 'width': 120},
      {'id': 'status', 'title': 'Status', 'data_key': 'status', 'width': 100},
      {'id': 'date', 'title': 'Date', 'data_key': 'published_at', 'width': 120},
      {'id': 'actions', 'title': 'Actions', 'data_key': None, 'width': 100}
    ]

    # Configure no posts label
    self.lbl_no_posts.text = "No blog posts yet. Click 'New Post' to create your first one!"
    self.lbl_no_posts.align = "center"
    self.lbl_no_posts.foreground = "#666666"
    self.lbl_no_posts.visible = False

    # Load posts
    self.load_posts()

  def load_posts(self, **event_args):
    """Load posts from server"""
    try:
      status_filter = self.dd_status_filter.selected_value
      search_term = self.txt_search.text or None

      # Call server to get posts
      posts = anvil.server.call('get_all_blog_posts', status_filter, search_term)

      if posts:
        self.dg_posts.items = posts
        self.dg_posts.visible = True
        self.lbl_no_posts.visible = False
      else:
        self.dg_posts.visible = False
        self.lbl_no_posts.visible = True

    except Exception as e:
      alert(f"Error loading posts: {str(e)}")

  def button_new_post_click(self, **event_args):
    """Create new post"""
    open_form('blog.BlogEditorForm', post_id=None)

  def dropdown_status_filter_change(self, **event_args):
    """Reload when filter changes"""
    self.load_posts()

  def button_search_click(self, **event_args):
    """Search posts"""
    self.load_posts()

  def textbox_search_pressed_enter(self, **event_args):
    """Search on Enter key"""
    self.load_posts()

  def dg_posts_row_click(self, row, **event_args):
    """Handle row actions"""
    # This will be handled by row template with edit/delete links
    pass

  @handle("btn_new_post", "click")
  def btn_new_post_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("dd_status_filter", "change")
  def dd_status_filter_change(self, **event_args):
    """This method is called when an item is selected"""
    pass

  @handle("btn_search", "click")
  def btn_search_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("txt_search", "pressed_enter")
  def txt_search_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    pass
