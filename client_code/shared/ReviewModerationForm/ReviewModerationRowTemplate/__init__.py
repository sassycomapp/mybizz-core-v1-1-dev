from ._anvil_designer import ReviewModerationRowTemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ReviewModerationRowTemplate(ReviewModerationRowTemplateTemplate):
  """Row template for review moderation"""

  def __init__(self, **properties):
    self.review = self.item
    self.init_components(**properties)

    # Display rating
    rating = self.review.get('rating', 0)
    self.lbl_rating.text = '⭐' * rating
    self.lbl_rating.font_size = 16

    # Display title
    self.lbl_title.text = self.review.get('title', 'No title')
    self.lbl_title.font_size = 16
    self.lbl_title.bold = True

    # Display reviewer info
    reviewer_name = self.review.get('reviewer_name', 'Anonymous')
    item_name = self.review.get('item_name', 'Unknown item')

    created_at = self.review.get('created_at')
    if created_at:
      date = created_at.strftime('%d %b %Y')
    else:
      date = 'Unknown date'

    self.lbl_reviewer_info.text = f"{reviewer_name} • {item_name} • {date}"
    self.lbl_reviewer_info.font_size = 12
    self.lbl_reviewer_info.foreground = "#666666"

    # Display comment
    self.lbl_comment.text = self.review.get('comment', '')
    self.lbl_comment.font_size = 14

    # Configure buttons
    self.btn_approve.text = "✅ Approve"
    self.btn_approve.role = "primary-color"

    self.btn_reject.text = "❌ Reject"
    self.btn_reject.role = "secondary-color"

    self.btn_spam.text = "🚩 Spam"
    self.btn_spam.role = "outlined-button"

    self.btn_respond.text = "💬 Respond"
    self.btn_respond.role = "outlined-button"

  def button_approve_click(self, **event_args):
    """Approve review"""
    try:
      result = anvil.server.call('approve_review', self.review.get_id())

      if result['success']:
        Notification("Review approved!", style="success").show()
        self.parent.raise_event('x-refresh')
      else:
        alert(f"Error: {result.get('error')}")

    except Exception as e:
      print(f"Error approving review: {e}")
      alert(f"Failed to approve: {str(e)}")

  def button_reject_click(self, **event_args):
    """Reject review"""
    reason = prompt("Rejection reason (optional):")

    try:
      result = anvil.server.call('reject_review', self.review.get_id(), reason)

      if result['success']:
        Notification("Review rejected", style="info").show()
        self.parent.raise_event('x-refresh')
      else:
        alert(f"Error: {result.get('error')}")

    except Exception as e:
      print(f"Error rejecting review: {e}")
      alert(f"Failed to reject: {str(e)}")

  def button_spam_click(self, **event_args):
    """Mark as spam"""
    if confirm("Mark this review as spam?"):
      try:
        result = anvil.server.call('mark_review_spam', self.review.get_id())

        if result['success']:
          Notification("Marked as spam", style="info").show()
          self.parent.raise_event('x-refresh')
        else:
          alert(f"Error: {result.get('error')}")

      except Exception as e:
        print(f"Error marking spam: {e}")
        alert(f"Failed to mark spam: {str(e)}")

  def button_respond_click(self, **event_args):
    """Add business response"""
    response = prompt("Your response to this review:")

    if response:
      try:
        result = anvil.server.call('add_business_response', self.review.get_id(), response)

        if result['success']:
          Notification("Response added!", style="success").show()
          self.parent.raise_event('x-refresh')
        else:
          alert(f"Error: {result.get('error')}")

      except Exception as e:
        print(f"Error adding response: {e}")
        alert(f"Failed to add response: {str(e)}")

  @handle("btn_approve", "click")
  def btn_approve_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_reject", "click")
  def btn_reject_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_spam", "click")
  def btn_spam_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_respond", "click")
  def btn_respond_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
