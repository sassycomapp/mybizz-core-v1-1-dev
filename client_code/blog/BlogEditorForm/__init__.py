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

class BlogEditorForm(BlogEditorFormTemplate):
  def __init__(self, post_id=None, **properties):
    self.post_id = post_id
    self.current_post = None
    self.init_components(**properties)

    # Configure title
    if self.post_id:
      self.lbl_title.text = "Edit Blog Post"
    else:
      self.lbl_title.text = "Create Blog Post"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True
    self.lbl_title.role = "headline"

    # Configure buttons
    self.btn_save_draft.text = "Save Draft"
    self.btn_save_draft.icon = "fa:save"
    self.btn_save_draft.role = "secondary-color"

    self.btn_publish.text = "Publish"
    self.btn_publish.icon = "fa:check"
    self.btn_publish.role = "primary-color"

    # Configure field labels
    self.lbl_title_field.text = "Title *"
    self.lbl_title_field.bold = True

    self.lbl_slug_field.text = "URL Slug (auto-generated)"
    self.lbl_slug_field.foreground = "#666666"
    self.lbl_slug_field.font_size = 12

    self.lbl_category_field.text = "Category"
    self.lbl_category_field.bold = True

    self.lbl_status_field.text = "Status"
    self.lbl_status_field.bold = True

    self.lbl_excerpt_field.text = "Excerpt (Short Summary)"
    self.lbl_excerpt_field.bold = True

    self.lbl_content_field.text = "Content *"
    self.lbl_content_field.bold = True

    self.lbl_image_field.text = "Featured Image"
    self.lbl_image_field.bold = True

    # Configure title field
    self.txt_title.placeholder = "Enter post title..."

    # Configure slug field
    self.txt_slug.placeholder = "auto-generated-from-title"
    self.txt_slug.enabled = True

    # Configure category dropdown
    self.load_categories()

    # Configure status dropdown
    self.dd_status.items = [
      ('Draft', 'draft'),
      ('Published', 'published')
    ]
    self.dd_status.selected_value = 'draft'

    # Configure excerpt
    self.txt_excerpt.placeholder = "Brief summary of the post (optional)..."
    self.txt_excerpt.rows = 3

    # Configure content
    self.txt_content.placeholder = "Write your post content here..."

    # Configure file uploader
    self.fu_featured_image.text = "Choose Image..."
    self.fu_featured_image.multiple = False

    # Configure current image label
    self.lbl_current_image.visible = False

    # Configure remove button
    self.btn_remove_image.text = ""
    self.btn_remove_image.icon = "fa:times"
    self.btn_remove_image.visible = False

    # Configure message label
    self.lbl_message.visible = False
    self.lbl_message.align = "center"

    # Load existing post if editing
    if self.post_id:
      self.load_post()

  def load_categories(self):
    """Load blog categories"""
    try:
      categories = anvil.server.call('get_blog_categories')
      self.dd_category.items = [('Uncategorized', None)] + [
        (cat['name'], cat.get_id()) for cat in categories
      ]
      self.dd_category.selected_value = None
    except Exception as e:
      print(f"Error loading categories: {e}")
      self.dd_category.items = [('Uncategorized', None)]

  def load_post(self):
    """Load existing post for editing"""
    try:
      self.current_post = anvil.server.call('get_blog_post', self.post_id)

      if self.current_post:
        self.txt_title.text = self.current_post['title']
        self.txt_slug.text = self.current_post['slug']
        self.txt_excerpt.text = self.current_post.get('excerpt', '')
        self.txt_content.content = self.current_post['content']
        self.dd_status.selected_value = self.current_post['status']

        if self.current_post.get('category_id'):
          self.dd_category.selected_value = self.current_post['category_id'].get_id()

        if self.current_post.get('featured_image'):
          self.lbl_current_image.text = "Current image uploaded"
          self.lbl_current_image.visible = True
          self.btn_remove_image.visible = True

    except Exception as e:
      alert(f"Error loading post: {str(e)}")
      open_form('blog.BlogListForm')

  def textbox_title_change(self, **event_args):
    """Auto-generate slug from title"""
    if self.txt_title.text and not self.post_id:
      self.txt_slug.text = self.generate_slug(self.txt_title.text)

  def generate_slug(self, title):
    """Convert title to URL-friendly slug"""
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars
    slug = re.sub(r'[-\s]+', '-', slug)    # Replace spaces with hyphens
    return slug.strip('-')

  def button_save_draft_click(self, **event_args):
    """Save as draft"""
    self.save_post('draft')

  def button_publish_click(self, **event_args):
    """Publish post"""
    self.save_post('published')

  def save_post(self, status):
    """Save blog post"""
    try:
      # Hide message
      self.lbl_message.visible = False

      # Validate
      if not self.txt_title.text:
        self.show_message("Title is required", "danger")
        return

      if not self.txt_content.content:
        self.show_message("Content is required", "danger")
        return

      if not self.txt_slug.text:
        self.txt_slug.text = self.generate_slug(self.txt_title.text)

      # Prepare data
      post_data = {
        'title': self.txt_title.text,
        'slug': self.txt_slug.text,
        'excerpt': self.txt_excerpt.text,
        'content': self.txt_content.content,
        'category_id': self.dd_category.selected_value,
        'status': status,
        'featured_image': self.fu_featured_image.file if self.fu_featured_image.file else None
      }

      # Save via server
      result = anvil.server.call(
        'save_blog_post',
        self.post_id,
        post_data
      )

      if result['success']:
        self.show_message(
          f"Post {'published' if status == 'published' else 'saved'} successfully!",
          "success"
        )

        # Return to list after 1 second
        anvil.server.call_s(lambda: open_form('blog.BlogListForm'))
      else:
        self.show_message(result['error'], "danger")

    except Exception as e:
      self.show_message(f"Error saving post: {str(e)}", "danger")

  def button_remove_image_click(self, **event_args):
    """Remove featured image"""
    self.lbl_current_image.visible = False
    self.btn_remove_image.visible = False
    self.fu_featured_image.file = None

  def show_message(self, text, style):
    """Display message"""
    self.lbl_message.text = text
    self.lbl_message.role = f"alert-{style}"
    self.lbl_message.visible = True

  @handle("btn_save_draft", "click")
  def btn_save_draft_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_publish", "click")
  def btn_publish_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("txt_title", "pressed_enter")
  def txt_title_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    pass

  @handle("btn_remove_image", "click")
  def btn_remove_image_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
