from ._anvil_designer import MessageRowTemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


from datetime import datetime

class MessageRowTemplate(MessageRowTemplateTemplate):
  """Message row in conversation thread"""

  def __init__(self, **properties):
    self.message = self.item
    self.init_components(**properties)

    # Determine message type
    author_type = self.message.get('author_type', 'customer')

    # Set icon based on author type
    if author_type == 'customer':
      icon = '👤'
      author_label = 'Customer'
    else:
      icon = '👨‍💼'
      author_label = 'Staff'

    # Format timestamp
    time_ago = self.format_time_ago(self.message['created_at'])

    # Build header
    header_text = f"{icon} {author_label} • {time_ago}"

    # Add internal note indicator
    if self.message.get('is_internal_note'):
      header_text += " (Internal Note)"
      self.col_message.background = "#FFF3CD"  # Yellow background for internal notes
    else:
      self.col_message.background = "#F9F9F9"  # Gray background for regular messages

    # Set header
    self.lbl_header.text = header_text
    self.lbl_header.font_size = 12
    self.lbl_header.foreground = "#666666"

    # Set message text
    self.lbl_message.text = self.message['message']
    self.lbl_message.font_size = 14

  def format_time_ago(self, dt):
    """
    Format datetime as relative time.
    
    Args:
      dt (datetime): Timestamp
      
    Returns:
      str: Relative time string (e.g. "2 hours ago")
    """
    if not dt:
      return "Unknown time"

    now = datetime.now()
    delta = now - dt

    if delta.days > 0:
      return f"{delta.days} day{'s' if delta.days > 1 else ''} ago"
    elif delta.seconds >= 3600:
      hours = delta.seconds // 3600
      return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif delta.seconds >= 60:
      minutes = delta.seconds // 60
      return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
      return "Just now"
