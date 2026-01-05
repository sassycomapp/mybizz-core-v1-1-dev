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
import re  # ← Only add this for slug generation

class LoginForm(LoginFormTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "Welcome Back"
    self.lbl_title.font_size = 24
    self.lbl_title.bold = True
    self.lbl_title.align = "center"
    self.lbl_title.role = "headline"

    # Configure subtitle
    self.lbl_subtitle.text = "Sign in to your account"
    self.lbl_subtitle.font_size = 14
    self.lbl_subtitle.align = "center"
    self.lbl_subtitle.foreground = "#666666"

    # Configure email field
    self.txt_email.placeholder = "Email address"
    self.txt_email.type = "email"
    self.txt_email.icon = "fa:envelope"

    # Configure password field
    self.txt_password.placeholder = "Password"
    self.txt_password.type = "password"
    self.txt_password.hide_text = True
    self.txt_password.icon = "fa:lock"

    # Configure forgot password link
    self.link_forgot_password.text = "Forgot Password?"
    self.link_forgot_password.align = "right"
    self.link_forgot_password.font_size = 12
    self.link_forgot_password.role = "secondary-color"

    # Configure login button
    self.btn_login.text = "Sign In"
    self.btn_login.icon = "fa:sign-in"
    self.btn_login.role = "primary-color"

    # Configure divider
    self.lbl_divider.text = "────── or ──────"
    self.lbl_divider.align = "center"
    self.lbl_divider.foreground = "#CCCCCC"
    self.lbl_divider.font_size = 12

    # Configure create account link
    self.link_create_account.text = "Create New Account"
    self.link_create_account.align = "center"
    self.link_create_account.font_size = 14
    self.link_create_account.role = "primary-color"

    # Configure error label (hidden by default)
    self.lbl_error.visible = False
    self.lbl_error.role = "alert-danger"
    self.lbl_error.align = "center"

  def button_login_click(self, **event_args):
    """Sign in using Anvil Users"""
    try:
      self.lbl_error.visible = False

      if not self.txt_email.text:
        self.show_error("Email is required")
        return

      if not self.txt_password.text:
        self.show_error("Password is required")
        return

      # Login with Anvil Users
      anvil.users.login_with_email(
        self.txt_email.text,
        self.txt_password.text
      )

      # Success - go to dashboard
      open_form('dashboard.DashboardForm')

    except anvil.users.AuthenticationFailed:
      self.show_error("Invalid email or password")
    except Exception as e:
      self.show_error(f"Login failed: {str(e)}")

  @handle("link_forgot_password", "click")
  def link_forgot_password_click(self, **event_args):
    """Navigate to password reset"""
    open_form('auth.PasswordResetForm')

  @handle("link_create_account", "click")
  def link_create_account_click(self, **event_args):
    """Navigate to signup"""
    open_form('auth.SignupForm')

  def show_error(self, message):
    """Display error message"""
    self.lbl_error.text = message
    self.lbl_error.visible = True

  @handle("btn_login", "click")
  def btn_login_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
