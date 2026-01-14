from ._anvil_designer import SocialShareComponentTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class SocialShareComponent(SocialShareComponentTemplate):
  """Social media sharing buttons"""

  def __init__(self, url=None, title=None, description=None, **properties):
    self.url = url or 'https://yourbusiness.com'
    self.title = title or 'Check this out!'
    self.description = description or ''

    self.init_components(**properties)

    # Configure label
    self.lbl_share.text = "Share this:"
    self.lbl_share.font_size = 14
    self.lbl_share.bold = True

    # Configure buttons
    self.btn_facebook.text = "Facebook"
    self.btn_facebook.icon = "fa:facebook"
    self.btn_facebook.role = "outlined-button"

    self.btn_twitter.text = "X"
    self.btn_twitter.icon = "fa:twitter"
    self.btn_twitter.role = "outlined-button"

    self.btn_linkedin.text = "LinkedIn"
    self.btn_linkedin.icon = "fa:linkedin"
    self.btn_linkedin.role = "outlined-button"

    self.btn_whatsapp.text = "WhatsApp"
    self.btn_whatsapp.icon = "fa:whatsapp"
    self.btn_whatsapp.role = "outlined-button"

    self.btn_email.text = "Email"
    self.btn_email.icon = "fa:envelope"
    self.btn_email.role = "outlined-button"

    self.btn_copy_link.text = "Copy Link"
    self.btn_copy_link.icon = "fa:link"
    self.btn_copy_link.role = "outlined-button"

  def generate_share_url(self, platform):
    """
    Generate platform-specific share URL.
    
    Args:
      platform (str): Platform name
      
    Returns:
      str: Share URL
    """
    encoded_url = urllib.parse.quote(self.url)
    encoded_title = urllib.parse.quote(self.title)
    encoded_description = urllib.parse.quote(self.description)

    urls = {
      'facebook': f'https://www.facebook.com/sharer/sharer.php?u={encoded_url}',
      'twitter': f'https://twitter.com/intent/tweet?url={encoded_url}&text={encoded_title}',
      'linkedin': f'https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}',
      'whatsapp': f'https://wa.me/?text={encoded_title}%20{encoded_url}',
      'email': f'mailto:?subject={encoded_title}&body={encoded_description}%20{encoded_url}'
    }

    return urls.get(platform, '')

  def button_facebook_click(self, **event_args):
    """Share on Facebook"""
    url = self.generate_share_url('facebook')
    anvil.js.window.open(url, '_blank', 'width=600,height=400')

  def button_twitter_click(self, **event_args):
    """Share on X (Twitter)"""
    url = self.generate_share_url('twitter')
    anvil.js.window.open(url, '_blank', 'width=600,height=400')

  def button_linkedin_click(self, **event_args):
    """Share on LinkedIn"""
    url = self.generate_share_url('linkedin')
    anvil.js.window.open(url, '_blank', 'width=600,height=400')

  def button_whatsapp_click(self, **event_args):
    """Share on WhatsApp"""
    url = self.generate_share_url('whatsapp')
    anvil.js.window.open(url, '_blank')

  def button_email_click(self, **event_args):
    """Share via Email"""
    url = self.generate_share_url('email')
    anvil.js.window.location.href = url

  def button_copy_link_click(self, **event_args):
    """Copy link (fallback method)"""
    # Show URL in alert for manual copy
    from anvil import TextBox
  
    txt = TextBox(text=self.url, width="100%")
    txt.select()
  
    alert(
      content=txt,
      title="Copy this link:",
      large=False
    )

  @handle("btn_facebook", "click")
  def btn_facebook_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_twitter", "click")
  def btn_twitter_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_linkedin", "click")
  def btn_linkedin_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_whatsapp", "click")
  def btn_whatsapp_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_email", "click")
  def btn_email_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_copy_link", "click")
  def btn_copy_link_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
