from ._anvil_designer import ReviewModerationFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ReviewModerationForm(ReviewModerationFormTemplate):
  """Review moderation for admin"""

  def __init__(self, **properties):
    self.init_components(**properties)

    # Check permissions
    user = anvil.users.get_user()
    if not user or user['role'] not in ['owner', 'manager']:
      alert("Access denied")
      open_form('dashboard.DashboardForm')
      return

    # Configure title
    self.lbl_title.text = "Review Moderation"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True

    # Configure pending count
    self.lbl_pending_count.font_size = 16
    self.lbl_pending_count.foreground = "#FF9800"

    # Load pending reviews
    self.load_pending_reviews()

  def load_pending_reviews(self):
    """Load pending reviews"""
    try:
      result = anvil.server.call('get_pending_reviews')

      if result['success']:
        reviews = result['data']

        # Update pending count
        self.lbl_pending_count.text = f"Pending ({len(reviews)})"

        # Load into repeating panel
        self.rp_reviews.items = reviews

      else:
        alert(f"Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
      print(f"Error loading reviews: {e}")
      alert(f"Failed to load pending reviews: {str(e)}")

  def refresh_reviews(self, **event_args):
    """Refresh the review list (called by child components)"""
    self.load_pending_reviews()