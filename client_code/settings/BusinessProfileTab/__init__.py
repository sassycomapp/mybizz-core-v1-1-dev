from ._anvil_designer import BusinessProfileTabTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables



class BusinessProfileTab(BusinessProfileTabTemplate):
  """Business profile settings tab"""

  def __init__(self, **properties):
    self.current_logo = None
    self.init_components(**properties)

    # Configure section title
    self.lbl_section_title.text = "Business Profile"
    self.lbl_section_title.font_size = 18
    self.lbl_section_title.bold = True

    # Configure fields
    self.txt_business_name.placeholder = "Your Business Name"

    self.txt_description.placeholder = "Describe your business..."
    self.txt_description.rows = 4

    self.lbl_logo.text = "Logo (max 2MB, .png or .jpg)"
    self.lbl_logo.font_size = 14

    self.txt_contact_email.placeholder = "contact@yourbusiness.com"
    self.txt_contact_email.type = "email"

    self.txt_phone.placeholder = "+1 (555) 123-4567"
    self.txt_phone.type = "tel"

    self.txt_address.placeholder = "123 Main Street\nCity, State ZIP\nCountry"
    self.txt_address.rows = 3

    self.txt_website.placeholder = "https://www.yourbusiness.com"

    # Social media
    self.lbl_social.text = "Social Media Links"
    self.lbl_social.font_size = 14
    self.lbl_social.bold = True

    self.txt_facebook.placeholder = "https://facebook.com/yourpage"
    self.txt_instagram.placeholder = "https://instagram.com/yourpage"
    self.txt_twitter.placeholder = "https://x.com/yourpage"
    self.txt_linkedin.placeholder = "https://linkedin.com/company/yourpage"

    # Save button
    self.btn_save.text = "Save Profile"
    self.btn_save.icon = "fa:save"
    self.btn_save.role = "primary-color"

    # Load current profile
    self.load_profile()

  def load_profile(self):
    """Load existing business profile"""
    try:
      result = anvil.server.call('get_business_profile')

      if result['success']:
        profile = result['data']

        if profile:
          self.txt_business_name.text = profile.get('business_name', '')
          self.txt_description.text = profile.get('description', '')
          self.txt_contact_email.text = profile.get('contact_email', '')
          self.txt_phone.text = profile.get('phone', '')
          self.txt_address.text = profile.get('address', '')
          self.txt_website.text = profile.get('website', '')

          # Social media
          social = profile.get('social_media', {})
          self.txt_facebook.text = social.get('facebook', '')
          self.txt_instagram.text = social.get('instagram', '')
          self.txt_twitter.text = social.get('twitter', '')
          self.txt_linkedin.text = social.get('linkedin', '')

          # Logo
          if profile.get('logo'):
            self.current_logo = profile['logo']
            self.img_logo_preview.source = profile['logo']
            self.img_logo_preview.height = 100
            self.img_logo_preview.visible = True
          else:
            self.img_logo_preview.visible = False

      else:
        print(f"Error loading profile: {result.get('error')}")

    except Exception as e:
      print(f"Error loading profile: {e}")

  @handle("file_logo", "change")
  def file_logo_change(self, file, **event_args):
    """Handle logo upload"""
    if file:
      # Check file size (2MB limit)
      if file.length > 2 * 1024 * 1024:
        alert("Logo file must be less than 2MB")
        return

      # Check file type
      if not file.content_type.startswith('image/'):
        alert("Logo must be an image file (.png or .jpg)")
        return

      # Show preview
      self.current_logo = file
      self.img_logo_preview.source = file
      self.img_logo_preview.height = 100
      self.img_logo_preview.visible = True

  def validate_profile(self):
    """Validate profile data"""
    if not self.txt_business_name.text:
      alert("Business name is required")
      return False

    if not self.txt_contact_email.text or '@' not in self.txt_contact_email.text:
      alert("Valid contact email is required")
      return False

    return True

  def button_save_click(self, **event_args):
    """Save business profile"""
    if not self.validate_profile():
      return

    try:
      profile_data = {
        'business_name': self.txt_business_name.text,
        'description': self.txt_description.text,
        'logo': self.current_logo,
        'contact_email': self.txt_contact_email.text,
        'phone': self.txt_phone.text,
        'address': self.txt_address.text,
        'website': self.txt_website.text,
        'social_media': {
          'facebook': self.txt_facebook.text,
          'instagram': self.txt_instagram.text,
          'twitter': self.txt_twitter.text,
          'linkedin': self.txt_linkedin.text
        }
      }

      result = anvil.server.call('save_business_profile', profile_data)

      if result['success']:
        Notification("Business profile saved successfully!", style="success").show()
      else:
        alert(f"Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
      print(f"Error saving profile: {e}")
      alert(f"Failed to save profile: {str(e)}")

  @handle("btn_save", "click")
  def btn_save_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
