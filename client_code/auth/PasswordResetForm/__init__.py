from ._anvil_designer import PasswordResetFormTemplate
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

class PasswordResetForm(PasswordResetFormTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "Reset Your Password"
    self.lbl_title.font_size = 24
    self.lbl_title.bold = True
    self.lbl_title.align = "center"
    self.lbl_title.role = "headline"

    # Configure subtitle
    self.lbl_subtitle.text = "Enter your email to receive reset link"
    self.lbl_subtitle.font_size = 14
    self.lbl_subtitle.align = "center"
    self.lbl_subtitle.foreground = "#666666"

    # Configure email field
    self.txt_email.placeholder = "Email address"
    self.txt_email.type = "email"
    self.txt_email.icon = "fa:envelope"

    # Configure send button
    self.btn_send_reset.text = "Send Reset Link"
    self.btn_send_reset.icon = "fa:paper-plane"
    self.btn_send_reset.role = "primary-color"

    # Configure success message (hidden by default)
    self.lbl_success.visible = False
    self.lbl_success.role = "alert-success"
    self.lbl_success.align = "center"

    # Configure error message (hidden by default)
    self.lbl_error.visible = False
    self.lbl_error.role = "alert-danger"
    self.lbl_error.align = "center"

    # Configure back link
    self.link_back_to_login.text = "← Back to Login"
    self.link_back_to_login.align = "center"
    self.link_back_to_login.font_size = 14
    self.link_back_to_login.role = "secondary-color"

  def button_send_reset_click(self, **event_args):
    """Send password reset email using Anvil Users"""
    try:
      # Hide previous messages
      self.lbl_success.visible = False
      self.lbl_error.visible = False

      # Validate email
      if not self.txt_email.text:
        self.show_error("Email is required")
        return

      # Send reset email using Anvil's built-in system
      anvil.users.send_password_reset_email(self.txt_email.text)

      # Show success message
      self.show_success(
        "Password reset link sent! Check your email."
      )

      # Clear email field
      self.txt_email.text = ""

    except anvil.users.UserNotFound:
      # Security: Don't reveal if email exists or not
      self.show_success(
        "If that email exists, a reset link has been sent."
      )
    except Exception as e:
      self.show_error(f"Failed to send reset email: {str(e)}")

  @handle("link_back_to_login", "click")
  def link_back_to_login_click(self, **event_args):
    """Navigate back to login"""
    open_form('auth.LoginForm')

  def show_success(self, message):
    """Display success message"""
    self.lbl_success.text = message
    self.lbl_success.visible = True
    self.lbl_error.visible = False

  def show_error(self, message):
    """Display error message"""
    self.lbl_error.text = message
    self.lbl_error.visible = True
    self.lbl_success.visible = False

  @handle("btn_send_reset", "click")
  def btn_send_reset_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
