from ._anvil_designer import LoginFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class LoginForm(LoginFormTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

   # Any code you write here will run before the form opens.
*****
from ._anvil_designer import LoginFormTemplate
from anvil import *
import anvil.users
import anvil.server

class LoginForm(LoginFormTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

  def button_login_click(self, **event_args):
    """Sign in with Anvil Users"""
    try:
      # Hide error
      self.lbl_error.visible = False

      # Validate inputs
      if not self.txt_email.text:
        self.show_error("Email is required")
        return
      if not self.txt_password.text:
        self.show_error("Password is required")
        return

      # Attempt login
      anvil.users.login_with_email(
        self.txt_email.text,
        self.txt_password.text
      )

      # Success - navigate to dashboard
      open_form('dashboard.DashboardForm')

    except anvil.users.AuthenticationFailed:
      self.show_error("Invalid email or password")
    except Exception as e:
      self.show_error(f"Login failed: {str(e)}")

  def link_forgot_password_click(self, **event_args):
    """Navigate to password reset"""
    open_form('auth.PasswordResetForm')

  def link_create_account_click(self, **event_args):
    """Navigate to signup"""
    open_form('auth.SignupForm')

  def show_error(self, message):
    """Display error message"""
    self.lbl_error.text = message
    self.lbl_error.visible = True