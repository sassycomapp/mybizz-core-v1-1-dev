from ._anvil_designer import BlogPostDetailFormTemplate
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

class BlogPostDetailForm(BlogPostDetailFormTemplate):
  def __init__(self, slug=None, **properties):
    self.slug = slug
    self.post = None
    self.init_components(**properties)

    # Configure back link
    self.link_back.text = "← Back to Blog"
    self.link_back.role = "secondary-color"

    # Configure title
    self.lbl_title.font_size = 32
    self.lbl_title.bold = True
    self.lbl_title.role = "headline"

    # Configure meta info
    self.lbl_meta.font_size = 14
    self.lbl_meta.foreground = "#666666"

    # Configure share section
    self.lbl_share_title.text = "Share this post:"
    self.lbl_share_title.bold = True
    self.lbl_share_title.font_size = 16

    # Configure views
    self.lbl_views.font_size = 12
    self.lbl_views.foreground = "#999999"
    self.lbl_views.icon = "fa:eye"

    # Configure not found message
    self.lbl_not_found.text = "Post not found or has been removed."
    self.lbl_not_found.align = "center"
    self.lbl_not_found.foreground = "#666666"
    self.lbl_not_found.visible = False

    # Load post
    if self.slug:
      self.load_post()
    else:
      self.show_not_found()

  def load_post(self):
    """Load blog post by slug"""
    try:
      # Get post and increment view count
      self.post = anvil.server.call('get_public_blog_post', self.slug)

      if not self.post:
        self.show_not_found()
        return

      # Display post data
      self.lbl_title.text = self.post['title']

      # Build meta info
      category = self.post.get('category_name', 'Uncategorized')
      date = self.post['published_at'].strftime('%B %d, %Y')
      author = self.post.get('author_name', 'Anonymous')
      self.lbl_meta.text = f"{category} • {date} • By {author}"

      # Display featured image
      if self.post.get('featured_image'):
        self.img_featured.source = self.post['featured_image']
        self.img_featured.height = 400
        self.img_featured.visible = True
      else:
        self.img_featured.visible = False

      # Display content
      self.rt_content.content = self.post['content']

      # Display view count
      self.lbl_views.text = f"{self.post['view_count']} views"

      # Create share buttons
      self.create_share_buttons()

    except Exception as e:
      print(f"Error loading post: {e}")
      self.show_not_found()

  def show_not_found(self):
    """Show not found message"""
    self.lbl_not_found.visible = True
    self.lbl_title.visible = False
    self.lbl_meta.visible = False
    self.img_featured.visible = False
    self.rt_content.visible = False
    self.lbl_share_title.visible = False
    self.fp_share_buttons.visible = False
    self.lbl_views.visible = False

  def create_share_buttons(self):
    """Create social share buttons"""
    # Get current page URL
    post_url = f"https://yourapp.anvil.app/blog/{self.slug}"
    post_title = self.post['title']

    # Facebook
    btn_facebook = Button(
      text="Facebook",
      icon="fa:facebook",
      role="secondary-color"
    )
    btn_facebook.set_event_handler(
      'click',
      lambda **e: self.share_on_platform('facebook', post_url, post_title)
    )

    # X (Twitter)
    btn_x = Button(
      text="X",
      icon="fa:twitter",
      role="secondary-color"
    )
    btn_x.set_event_handler(
      'click',
      lambda **e: self.share_on_platform('x', post_url, post_title)
    )

    # LinkedIn
    btn_linkedin = Button(
      text="LinkedIn",
      icon="fa:linkedin",
      role="secondary-color"
    )
    btn_linkedin.set_event_handler(
      'click',
      lambda **e: self.share_on_platform('linkedin', post_url, post_title)
    )

    # WhatsApp
    btn_whatsapp = Button(
      text="WhatsApp",
      icon="fa:whatsapp",
      role="secondary-color"
    )
    btn_whatsapp.set_event_handler(
      'click',
      lambda **e: self.share_on_platform('whatsapp', post_url, post_title)
    )

    # Copy Link
    btn_copy = Button(
      text="Copy Link",
      icon="fa:link",
      role="secondary-color"
    )
    btn_copy.set_event_handler(
      'click',
      lambda **e: self.copy_link(post_url)
    )

    # Add to panel
    self.fp_share_buttons.clear()
    self.fp_share_buttons.add_component(btn_facebook)
    self.fp_share_buttons.add_component(btn_x)
    self.fp_share_buttons.add_component(btn_linkedin)
    self.fp_share_buttons.add_component(btn_whatsapp)
    self.fp_share_buttons.add_component(btn_copy)

  def share_on_platform(self, platform, url, title):
    """Open share URL for platform"""
    share_urls = {
      'facebook': f"https://www.facebook.com/sharer/sharer.php?u={url}",
      'x': f"https://twitter.com/intent/tweet?url={url}&text={title}",
      'linkedin': f"https://www.linkedin.com/sharing/share-offsite/?url={url}",
      'whatsapp': f"https://wa.me/?text={title} {url}"
    }

    if platform in share_urls:
      anvil.js.window.open(share_urls[platform], '_blank')

  def copy_link(self, url):
    """Copy link to clipboard"""
    try:
      anvil.js.window.navigator.clipboard.writeText(url)
      Notification("Link copied to clipboard!", style="success", timeout=2).show()
    except:
      # Fallback for browsers without clipboard API
      alert(f"Copy this link:\n{url}", title="Share Link")

  @handle("link_back", "click")
  def link_back_click(self, **event_args):
    """Navigate back to blog list"""
    open_form('blog.PublicBlogForm')