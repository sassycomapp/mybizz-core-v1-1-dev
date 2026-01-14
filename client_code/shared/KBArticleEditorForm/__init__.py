from ._anvil_designer import KBArticleEditorFormTemplate
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

class KBArticleEditorForm(KBArticleEditorFormTemplate):
  """Knowledge base article editor"""

  def __init__(self, article_id=None, **properties):
    self.article_id = article_id
    self.init_components(**properties)

    # Check permissions
    user = anvil.users.get_user()
    if not user or user['role'] not in ['owner', 'manager']:
      alert("Access denied")
      return

    self.lbl_title.text = "Knowledge Base Article Editor"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True

    # Title
    self.txt_title.placeholder = "Article Title"

    # Slug (auto-generated from title)
    self.txt_slug.placeholder = "url-friendly-slug"

    # Category dropdown
    self.load_categories()

    # Excerpt
    self.txt_excerpt.placeholder = "Brief summary (shown in search results)"
    self.txt_excerpt.rows = 2

    # Content (rich text)
    self.rt_content.placeholder = "Write your article content here..."
    self.rt_content.enable_slots = True

    # Keywords
    self.txt_keywords.placeholder = "comma, separated, keywords"

    # Published checkbox
    self.cb_published.text = "Published"

    # Buttons
    self.btn_save_draft.text = "Save Draft"
    self.btn_save_draft.icon = "fa:save"
    self.btn_save_draft.role = "outlined-button"

    self.btn_publish.text = "Publish"
    self.btn_publish.icon = "fa:check"
    self.btn_publish.role = "primary-color"

    self.btn_preview.text = "Preview"
    self.btn_preview.icon = "fa:eye"
    self.btn_preview.role = "outlined-button"

    # Load article if editing
    if article_id:
      self.load_article()

  def load_categories(self):
    """Load KB categories"""
    try:
      result = anvil.server.call('get_kb_categories')

      if result['success']:
        categories = result['data']
        items = [(c['name'], c.get_id()) for c in categories]
        self.dd_category.items = items

    except Exception as e:
      print(f"Error loading categories: {e}")

  def load_article(self):
    """Load existing article"""
    try:
      result = anvil.server.call('get_kb_article', self.article_id)

      if result['success']:
        article = result['data']

        self.txt_title.text = article['title']
        self.txt_slug.text = article['slug']
        self.dd_category.selected_value = article['category_id'].get_id()
        self.txt_excerpt.text = article.get('excerpt', '')
        self.rt_content.content = article.get('content', '')

        keywords = article.get('keywords', [])
        self.txt_keywords.text = ', '.join(keywords) if keywords else ''

        self.cb_published.checked = article.get('published', False)

    except Exception as e:
      alert(f"Failed to load article: {str(e)}")

  def txt_title_change(self, **event_args):
    """Auto-generate slug from title"""
    if not self.article_id:  # Only auto-generate for new articles
      title = self.txt_title.text
      slug = self.generate_slug(title)
      self.txt_slug.text = slug

  def generate_slug(self, text):
    """Generate URL-friendly slug"""
    if not text:
      return ''

    # Convert to lowercase
    slug = text.lower()

    # Replace spaces with hyphens
    slug = slug.replace(' ', '-')

    # Remove special characters
    slug = re.sub(r'[^a-z0-9\-]', '', slug)

    # Remove duplicate hyphens
    slug = re.sub(r'-+', '-', slug)

    # Remove leading/trailing hyphens
    slug = slug.strip('-')

    return slug

  def validate_article(self):
    """Validate article data"""
    if not self.txt_title.text:
      alert("Please enter a title")
      return False

    if not self.txt_slug.text:
      alert("Please enter a slug")
      return False

    if not self.dd_category.selected_value:
      alert("Please select a category")
      return False

    if not self.rt_content.content:
      alert("Please enter article content")
      return False

    return True

  def get_article_data(self):
    """Get article data from form"""
    # Parse keywords
    keywords_text = self.txt_keywords.text
    keywords = [k.strip() for k in keywords_text.split(',') if k.strip()]

    return {
      'title': self.txt_title.text,
      'slug': self.txt_slug.text,
      'category_id': self.dd_category.selected_value,
      'excerpt': self.txt_excerpt.text,
      'content': self.rt_content.content,
      'keywords': keywords,
      'published': self.cb_published.checked
    }

  def button_save_draft_click(self, **event_args):
    """Save as draft"""
    if not self.validate_article():
      return

    # Ensure not published
    self.cb_published.checked = False

    self.save_article()

  def button_publish_click(self, **event_args):
    """Publish article"""
    if not self.validate_article():
      return

    # Ensure published
    self.cb_published.checked = True

    self.save_article()

  def save_article(self):
    """Save article"""
    try:
      article_data = self.get_article_data()

      if self.article_id:
        result = anvil.server.call('update_kb_article', self.article_id, article_data)
      else:
        result = anvil.server.call('create_kb_article', article_data)

      if result['success']:
        status = "published" if article_data['published'] else "saved as draft"
        Notification(f"Article {status}!", style="success").show()

        if not self.article_id:
          self.article_id = result['article_id']
      else:
        alert(f"Error: {result.get('error')}")

    except Exception as e:
      alert(f"Failed to save: {str(e)}")

  def button_preview_click(self, **event_args):
    """Preview article"""
    # TODO: Show preview in modal
    Notification("Preview feature coming soon", style="info").show()

  @handle("txt_title", "pressed_enter")
  def txt_title_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    pass

  @handle("btn_save_draft", "click")
  def btn_save_draft_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_publish", "click")
  def btn_publish_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_preview", "click")
  def btn_preview_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
