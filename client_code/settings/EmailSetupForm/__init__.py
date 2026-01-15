from ._anvil_designer import EmailSetupFormTemplate
from anvil import *
from routing import router
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class EmailSetupForm(EmailSetupFormTemplate):
  """Zoho email setup form (for founder use during onboarding)"""

  def __init__(self, **properties):
    self.init_components(**properties)

    self.lbl_title.text = "Email Setup (Zoho Configuration)"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True

    self.lbl_info.text = "ℹ️ This form is used during client onboarding to configure email."
    self.lbl_info.foreground = "#2196F3"

    # Domain input
    self.txt_domain.placeholder = "clientdomain.com"

    # Business name (auto-filled)
    self.txt_business_name.placeholder = "Business Name"
    self.load_business_name()

    # Email addresses label
    self.lbl_emails.text = "Email Addresses to Create:"
    self.lbl_emails.bold = True
    self.lbl_emails.font_size = 14

    # Buttons
    self.btn_generate_dns.text = "Generate DNS Records"
    self.btn_generate_dns.icon = "fa:file-text"
    self.btn_generate_dns.role = "outlined-button"

    self.btn_test.text = "Test Configuration"
    self.btn_test.icon = "fa:check-circle"
    self.btn_test.role = "primary-color"

  def load_business_name(self):
    """Load business name from profile"""
    try:
      result = anvil.server.call('get_business_profile')

      if result['success'] and result['data']:
        self.txt_business_name.text = result['data'].get('business_name', '')

    except Exception as e:
      print(f"Error loading business name: {e}")

  def button_generate_dns_click(self, **event_args):
    """Generate DNS records for display"""
    domain = self.txt_domain.text

    if not domain:
      alert("Please enter a domain")
      return

    try:
      result = anvil.server.call('generate_dns_records', domain)

      if result['success']:
        records = result['data']

        # Display DNS records in modal
        dns_text = "\n".join([
          f"{record['type']}: {record['value']}"
          for record in records
        ])

        alert(
          content=Label(text=dns_text, font="monospace"),
          title="DNS Records to Add",
          large=True
        )
      else:
        alert(f"Error: {result.get('error')}")

    except Exception as e:
      alert(f"Failed: {str(e)}")

  def button_test_click(self, **event_args):
    """Test email configuration"""
    try:
      result = anvil.server.call('test_email_configuration')

      if result['success']:
        Notification("Email configuration working!", style="success").show()
      else:
        alert(f"Test failed: {result.get('error')}")

    except Exception as e:
      alert(f"Test failed: {str(e)}")

  @handle("btn_generate_dns", "click")
  def btn_generate_dns_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_test", "click")
  def btn_test_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
