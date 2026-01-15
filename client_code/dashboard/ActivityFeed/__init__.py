from ._anvil_designer import ActivityFeedTemplate
from anvil import *
from routing import router
import anvil.server
import anvil.users
from datetime import datetime

class ActivityFeed(ActivityFeedTemplate):
  """Recent activity timeline widget"""

  def __init__(self, **properties):
    self.current_limit = 10
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "Recent Activity"
    self.lbl_title.font_size = 18
    self.lbl_title.bold = True

    # Configure refresh button
    self.btn_refresh.text = ""
    self.btn_refresh.icon = "fa:refresh"
    self.btn_refresh.role = "outlined-button"

    # Configure no activity label
    self.lbl_no_activity.text = "No recent activity"
    self.lbl_no_activity.align = "center"
    self.lbl_no_activity.foreground = "#666666"
    self.lbl_no_activity.visible = False

    # Configure load more button
    self.btn_load_more.text = "Load More"
    self.btn_load_more.role = "outlined-button"
    self.btn_load_more.visible = False

    # Set repeating panel template
    self.rp_activities.item_template = 'dashboard.ActivityItemTemplate'

    # Load activities
    self.load_activities()

  def load_activities(self):
    """Load recent activity"""
    try:
      # Get activities from server
      result = anvil.server.call('get_recent_activity', self.current_limit)

      if result['success']:
        activities = result['data']

        if activities:
          # Format activities for display
          formatted_activities = []
          for activity in activities:
            formatted_activities.append({
              'icon': self.get_activity_icon(activity['type']),
              'description': activity['description'],
              'time_ago': self.format_time_ago(activity['timestamp'])
            })

          self.rp_activities.items = formatted_activities
          self.rp_activities.visible = True
          self.lbl_no_activity.visible = False

          # Show load more if there might be more activities
          self.btn_load_more.visible = len(activities) >= self.current_limit

        else:
          self.rp_activities.visible = False
          self.lbl_no_activity.visible = True
          self.btn_load_more.visible = False

      else:
        alert(f"Error loading activity: {result.get('error', 'Unknown error')}")

    except Exception as e:
      print(f"Error loading activities: {e}")
      alert(f"Failed to load activities: {str(e)}")

  def get_activity_icon(self, activity_type):
    """Get emoji icon for activity type"""
    icons = {
      'booking': '📅',
      'order': '🛒',
      'checkout': '✅',
      'customer': '👤',
      'blog': '📝',
      'payment': '💳',
      'review': '⭐',
      'ticket': '🎫'
    }
    return icons.get(activity_type, '•')

  def format_time_ago(self, timestamp):
    """Format timestamp as relative time"""
    if not timestamp:
      return ""

    try:
      now = datetime.now()
      diff = now - timestamp

      seconds = diff.total_seconds()

      if seconds < 60:
        return "just now"
      elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} min{'s' if minutes != 1 else ''} ago"
      elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
      elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
      else:
        return timestamp.strftime('%b %d, %Y')

    except Exception as e:
      print(f"Error formatting time: {e}")
      return ""

  def button_refresh_click(self, **event_args):
    """Refresh activity feed"""
    self.current_limit = 10
    self.load_activities()

  def button_load_more_click(self, **event_args):
    """Load more activities"""
    self.current_limit += 10
    self.load_activities()

  @handle("btn_refresh", "click")
  def btn_refresh_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_load_more", "click")
  def btn_load_more_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
