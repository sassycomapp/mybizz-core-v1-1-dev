import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .NotificationComponent import NotificationComponent

# Global container for notifications
_notification_container = None

def initialize_notification_container():
  """
  Initialize the notification container.
  Call this once when the app starts (in startup module or first form).
  """
  global _notification_container

  if _notification_container is None:
    _notification_container = ColumnPanel()
    _notification_container.spacing = 'small'

    # Position in top-right corner
    _notification_container.role = 'notification-container'

  return _notification_container

def show_notification(message, notification_type="info", duration=5):
  """
  Show a toast notification.
  
  Args:
    message (str): Notification message
    notification_type (str): 'success', 'warning', 'error', or 'info'
    duration (int): Seconds before auto-dismiss (0 = manual dismiss only)
  
  Returns:
    NotificationComponent: The created notification
  """
  try:
    # Ensure container exists
    container = initialize_notification_container()

    # Create notification
    notification = NotificationComponent(
      message=message,
      notification_type=notification_type,
      duration=duration
    )

    # Add to container at the top
    container.add_component(notification, index=0)

    # Ensure container is visible on current form
    current_form = get_open_form()
    if current_form and container not in current_form.get_components():
      # Add container to current form if not already there
      if hasattr(current_form, 'add_component'):
        current_form.add_component(container)

    return notification

  except Exception as e:
    print(f"Error showing notification: {e}")
    # Fallback to alert
    alert(message)
    return None

def clear_notifications():
  """Clear all active notifications"""
  global _notification_container

  if _notification_container:
    _notification_container.clear()