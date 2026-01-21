from ._anvil_designer import BlankLayoutTemplate
from anvil import *
import anvil.server
from routing import router
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class BlankLayout(BlankLayoutTemplate):
  def __init__(self, content_form=None, show_logo=False, page_title=None, **properties):
    self.init_components(**properties)
    self.current_content = None

    # Set page title
    if page_title:
      self.set_title(page_title)

    # Configure logo (optional)
    if show_logo:
      # self.img_logo.source = "logo.png"  # Upload to Assets
      self.img_logo.height = 60
      self.img_logo.visible = True
      self.img_logo.align = "center"
    else:
      self.img_logo.visible = False

    # Configure card container
    self.card_container.spacing_above = "large"
    self.card_container.spacing_below = "large"
    self.card_container.align = "center"
    self.card_container.background = "white"
    self.card_container.role = "card"

    # Style the card
    # In Anvil, you'd set these in the designer
    # card_container:
    #   - border_radius: 8px
    #   - box_shadow: 0 4px 12px rgba(0,0,0,0.1)
    #   - max_width: 500px
    #   - padding: 40px

    # Configure footer
    self.build_footer()

    # Load content form
    if content_form:
      self.load_content(content_form)

  def build_footer(self):
    """Build simple footer with legal links"""
    # Copyright
    self.lbl_copyright.text = "© 2026 MyBizz. All rights reserved."
    self.lbl_copyright.font_size = 12
    self.lbl_copyright.foreground = "#999999"
    self.lbl_copyright.align = "center"

    # Legal links
    legal_links = [
      {'label': 'Privacy Policy', 'url': '/privacy'},
      {'label': 'Terms of Service', 'url': '/terms'},
      {'label': 'Contact', 'url': '/contact'}
    ]

    self.flow_legal_links.clear()

    for i, link_item in enumerate(legal_links):
      if i > 0:
        # Add separator
        separator = Label(
          text=" | ",
          foreground="#999999",
          font_size=12
        )
        self.flow_legal_links.add_component(separator)

      link = Link(
        text=link_item['label'],
        url_hash=link_item['url'],
        foreground="#999999",
        font_size=12
      )
      self.flow_legal_links.add_component(link)

    # Center legal links
    self.flow_legal_links.align = "center"

  def load_content(self, content_form):
    """
    Load a form into the content area
    
    Args:
        content_form (str or Form): Form class name or instance
    """
    self.content_panel.clear()

    try:
      if isinstance(content_form, str):
        # String form path
        placeholder = Label(
          text=f"Loading: {content_form}",
          align="center",
          font_size=18
        )
        self.content_panel.add_component(placeholder)
      else:
        # Form instance
        self.content_panel.add_component(content_form)

      self.current_content = content_form

    except Exception as e:
      error_label = Label(
        text=f"Error loading content: {str(e)}",
        foreground="red",
        align="center"
      )
      self.content_panel.add_component(error_label)

  def set_title(self, title):
    """
    Set page title (browser tab)
    
    Args:
        title (str): Page title
    """
    # In Anvil, this would set the browser title
    pass

  def show_loading(self, message="Loading..."):
    """
    Show loading indicator
    
    Args:
        message (str): Loading message
    """
    self.content_panel.clear()

    # Add loading spinner and message
    loading_label = Label(
      text=message,
      align="center",
      font_size=16,
      foreground="#666666"
    )

    self.content_panel.add_component(loading_label)

    # Could add animated spinner here

  def show_error(self, message):
    """
    Show error message
    
    Args:
        message (str): Error message
    """
    self.content_panel.clear()

    error_label = Label(
      text=f"⚠️ {message}",
      align="center",
      font_size=16,
      foreground="#F44336"
    )

    self.content_panel.add_component(error_label)

  def get_current_content(self):
    """
    Get currently loaded content form
    
    Returns:
        Form: Current content form instance
    """
    return self.current_content