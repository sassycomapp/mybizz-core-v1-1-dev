from ._anvil_designer import SignupFormTemplate
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

class SignupForm(SignupFormTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "Create Your Account"
    self.lbl_title.font_size = 24
    self.lbl_title.bold = True
    self.lbl_title.align = "center"
    self.lbl_title.role = "headline"

    # Configure subtitle
    self.lbl_subtitle.text = "Start your business journey today"
    self.lbl_subtitle.font_size = 14
    self.lbl_subtitle.align = "center"
    self.lbl_subtitle.foreground = "#666666"

    # Configure business name field
    self.txt_business_name.placeholder = "Business Name"
    self.txt_business_name.icon = "fa:building"

    # Configure email field
    self.txt_email.placeholder = "Email address"
    self.txt_email.type = "email"
    self.txt_email.icon = "fa:envelope"

    # Configure password field
    self.txt_password.placeholder = "Password (minimum 6 characters)"
    self.txt_password.type = "password"
    self.txt_password.hide_text = True
    self.txt_password.icon = "fa:lock"

    # Configure confirm password field
    self.txt_confirm_password.placeholder = "Confirm Password"
    self.txt_confirm_password.type = "password"
    self.txt_confirm_password.hide_text = True
    self.txt_confirm_password.icon = "fa:lock"

    # Configure create account button
    self.btn_create_account.text = "Create Account"
    self.btn_create_account.icon = "fa:sparkles"
    self.btn_create_account.role = "primary-color"

    # Configure error label (hidden by default)
    self.lbl_error.visible = False
    self.lbl_error.role = "alert-danger"
    self.lbl_error.align = "center"

    # Configure sign in link
    self.link_sign_in.text = "Already have an account? Sign In"
    self.link_sign_in.align = "center"
    self.link_sign_in.font_size = 14
    self.link_sign_in.role = "secondary-color"

  def button_create_account_click(self, **event_args):
    """Create new account"""
    try:
      # Hide error
      self.lbl_error.visible = False

      # Validate inputs
      if not self.txt_business_name.text:
        self.show_error("Business name is required")
        return

      if not self.txt_email.text:
        self.show_error("Email is required")
        return

      if not self.validate_email(self.txt_email.text):
        self.show_error("Please enter a valid email address")
        return

      if not self.txt_password.text:
        self.show_error("Password is required")
        return

      if len(self.txt_password.text) < 6:
        self.show_error("Password must be at least 6 characters")
        return

      if self.txt_password.text != self.txt_confirm_password.text:
        self.show_error("Passwords do not match")
        return

      # Create account via server
      result = anvil.server.call(
        'create_account',
        self.txt_email.text,
        self.txt_password.text,
        self.txt_business_name.text
      )

      if result['success']:
        # Auto-login the new user
        anvil.users.login_with_email(
          self.txt_email.text,
          self.txt_password.text
        )

        # Navigate to dashboard
        open_form('dashboard.DashboardForm')
      else:
        self.show_error(result['error'])

    except Exception as e:
      self.show_error(f"Signup failed: {str(e)}")

  @handle("link_sign_in", "click")
  def link_sign_in_click(self, **event_args):
    """Navigate to login"""
    open_form('auth.LoginForm')

  def validate_email(self, email):
    """Basic email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

  def show_error(self, message):
    """Display error message"""
    self.lbl_error.text = message
    self.lbl_error.visible = True

  @handle("btn_create_account", "click")
  def btn_create_account_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
