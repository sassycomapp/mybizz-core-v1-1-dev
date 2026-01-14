from ._anvil_designer import NotificationComponentTemplate
from anvil import *
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

  def __init__(self, **properties):
    self.init_components(**properties)

    # Default styling
    self.col_notification.spacing = 'small'
    self.col_notification.visible = False

  def show_notification(self, message, notification_type='info', duration=5):
    """
    Show notification toast.
    
    Args:
      message (str): Notification message
      notification_type (str): 'success', 'warning', 'error', 'info'
      duration (int): Seconds before auto-dismiss (0 = no auto-dismiss)
    """
    # Set icon based on type
    icons = {
      'success': '✅',
      'warning': '⚠️',
      'error': '❌',
      'info': 'ℹ️'
    }

    # Set colors based on type
    colors = {
      'success': '#4CAF50',
      'warning': '#FF9800',
      'error': '#F44336',
      'info': '#2196F3'
    }

    # Configure notification
    self.lbl_icon.text = icons.get(notification_type, 'ℹ️')
    self.lbl_icon.font_size = 20

    self.lbl_message.text = message
    self.lbl_message.font_size = 14

    # Set border color
    border_color = colors.get(notification_type, '#2196F3')
    self.col_notification.border = f"2px solid {border_color}"

    # Show notification
    self.col_notification.visible = True

    # Auto-dismiss if duration > 0
    if duration > 0:
      self.timer_auto_dismiss.interval = duration
      self.timer_auto_dismiss.enabled = True

  @handle("timer_auto_dismiss", "tick")
  def timer_auto_dismiss_tick(self, **event_args):
    """Auto-dismiss notification"""
    self.hide_notification()
    self.timer_auto_dismiss.enabled = False

  def hide_notification(self):
    """Hide notification"""
    self.col_notification.visible = False

  def col_notification_click(self, **event_args):
    """Allow user to dismiss by clicking"""
    self.hide_notification()