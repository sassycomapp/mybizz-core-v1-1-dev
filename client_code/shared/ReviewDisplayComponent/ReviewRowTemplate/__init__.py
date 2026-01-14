from ._anvil_designer import ReviewRowTemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ReviewRowTemplate(ReviewRowTemplateTemplate):
  """Single review row"""

  def __init__(self, **properties):
    self.review = self.item
    self.init_components(**properties)

    # Display stars
    rating = self.review.get('rating', 0)
    self.lbl_stars.text = '⭐' * rating + '☆' * (5 - rating)
    self.lbl_stars.font_size = 16

    # Display title
    self.lbl_title.text = self.review.get('title', 'No title')
    self.lbl_title.font_size = 16
    self.lbl_title.bold = True

    # Display reviewer info
    reviewer_name = self.review.get('reviewer_name', 'Anonymous')
    verified = '✅ Verified Purchase • ' if self.review.get('is_verified_purchase') else ''

    created_at = self.review.get('created_at')
    if created_at:
      date = created_at.strftime('%d %b %Y')
    else:
      date = 'Unknown date'

    self.lbl_reviewer.text = f"{reviewer_name} • {verified}{date}"
    self.lbl_reviewer.foreground = "#666666"
    self.lbl_reviewer.font_size = 12

    # Display comment
    self.lbl_comment.text = self.review.get('comment', '')
    self.lbl_comment.font_size = 14

    # Helpful button
    helpful_count = self.review.get('helpful_count', 0)
    self.btn_helpful.text = f"👍 Helpful ({helpful_count})"
    self.btn_helpful.role = "outlined-button"

    # Report button
    self.btn_report.text = "🚩 Report"
    self.btn_report.role = "outlined-button"

    # Business response
    response = self.review.get('business_response')
    if response:
      self.col_response.visible = True
      self.lbl_response.text = f"💬 Business Response:\n   {response}"
      self.lbl_response.foreground = "#2196F3"
      self.lbl_response.italic = True
    else:
      self.col_response.visible = False

  def button_helpful_click(self, **event_args):
    """Mark review as helpful"""
    try:
      result = anvil.server.call('mark_review_helpful', self.review.get_id())

      if result['success']:
        # Update count
        self.review['helpful_count'] = self.review.get('helpful_count', 0) + 1
        self.btn_helpful.text = f"👍 Helpful ({self.review['helpful_count']})"
        Notification("Thank you for your feedback!", style="success").show()

      else:
        alert(f"Error: {result.get('error')}")

    except Exception as e:
      print(f"Error marking helpful: {e}")
      alert(f"Failed to mark helpful: {str(e)}")

  def button_report_click(self, **event_args):
    """Report review as inappropriate"""
    reason = prompt("Why are you reporting this review?")

    if reason:
      try:
        result = anvil.server.call('report_review', self.review.get_id(), reason)

        if result['success']:
          Notification("Review reported. Thank you!", style="success").show()
        else:
          alert(f"Error: {result.get('error')}")

      except Exception as e:
        print(f"Error reporting review: {e}")
        alert(f"Failed to report: {str(e)}")

  @handle("btn_helpful", "click")
  def btn_helpful_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_report", "click")
  def btn_report_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
