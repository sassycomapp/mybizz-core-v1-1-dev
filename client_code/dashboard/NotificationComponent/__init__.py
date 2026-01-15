from ._anvil_designer import NotificationComponentTemplate
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


class NotificationComponent(NotificationComponentTemplate):
  """Toast notification component"""

  def __init__(self, message="", notification_type="info", duration=5, **properties):
    self.init_components(**properties)

    # Configure based on type
    self.notification_type = notification_type
    self.duration = duration

    # Set icon
    icons = {
      'success': '✅',
      'warning': '⚠️',
      'error': '❌',
      'info': 'ℹ️'
    }
    self.lbl_icon.text = icons.get(notification_type, 'ℹ️')
    self.lbl_icon.font_size = 18

    # Set message
    self.lbl_message.text = message
    self.lbl_message.font_size = 14

    # Set close button
    self.link_close.text = "×"
    self.link_close.font_size = 20
    self.link_close.foreground = "#666666"

    # Set colors based on type
    colors = {
      'success': {'bg': '#D4EDDA', 'fg': '#155724'},
      'warning': {'bg': '#FFF3CD', 'fg': '#856404'},
      'error': {'bg': '#F8D7DA', 'fg': '#721C24'},
      'info': {'bg': '#D1ECF1', 'fg': '#0C5460'}
    }

    style = colors.get(notification_type, colors['info'])
    self.background = style['bg']
    self.foreground = style['fg']
    self.lbl_message.foreground = style['fg']

    # Auto-dismiss after duration
    if duration > 0:
      self.timer = Timer(interval=duration)
      self.timer.tick = self.dismiss

  def dismiss(self, **event_args):
    """Dismiss the notification"""
    try:
      # Stop timer
      if hasattr(self, 'timer'):
        self.timer.interval = 0

      # Remove from parent
      if self.parent:
        self.parent.remove_from_parent()
    except Exception as e:
      print(f"Error dismissing notification: {e}")

  @handle("link_close", "click")
  def link_close_click(self, **event_args):
    """Close notification when X is clicked"""
    self.dismiss()
