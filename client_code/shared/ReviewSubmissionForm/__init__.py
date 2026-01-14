from ._anvil_designer import ReviewSubmissionFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ReviewSubmissionForm(ReviewSubmissionFormTemplate):
  """Review submission form for customers"""

  def __init__(self, item_type=None, item_id=None, **properties):
    self.item_type = item_type  # 'product', 'service', 'booking'
    self.item_id = item_id
    self.rating = 5  # Default to 5 stars

    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "Write a Review"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True

    # Configure rating display
    self.lbl_rating.font_size = 16
    self.update_rating_display()

    # Configure star links
    for i, star_link in enumerate([self.lnk_star_1, self.lnk_star_2, 
                                   self.lnk_star_3, self.lnk_star_4, 
                                   self.lnk_star_5], 1):
      star_link.text = "⭐"
      star_link.font_size = 32
      star_link.tag = i  # Store star number

    # Configure title input
    self.txt_title.placeholder = "Summarize your experience"

    # Configure review text
    self.txt_review.placeholder = "Share your thoughts about this product/service"
    self.txt_review.rows = 5

    # Configure submit button
    self.btn_submit.text = "Submit Review"
    self.btn_submit.icon = "fa:star"
    self.btn_submit.role = "primary-color"

  def update_rating_display(self):
    """Update rating display with filled/empty stars"""
    filled_stars = '⭐' * self.rating
    empty_stars = '☆' * (5 - self.rating)
    self.lbl_rating.text = f"Rating: {filled_stars}{empty_stars} ({self.rating}/5)"

    # Update star link colors to show selection
    for i, star_link in enumerate([self.lnk_star_1, self.lnk_star_2, 
                                   self.lnk_star_3, self.lnk_star_4, 
                                   self.lnk_star_5], 1):
      if i <= self.rating:
        star_link.foreground = "#FFD700"  # Gold for selected
      else:
        star_link.foreground = "#CCCCCC"  # Gray for unselected

  def star_click(self, star_number, **event_args):
    """Handle star click to set rating"""
    self.rating = star_number
    self.update_rating_display()

  def link_star_1_click(self, **event_args):
    """Set rating to 1 star"""
    self.star_click(1)

  def link_star_2_click(self, **event_args):
    """Set rating to 2 stars"""
    self.star_click(2)

  def link_star_3_click(self, **event_args):
    """Set rating to 3 stars"""
    self.star_click(3)

  def link_star_4_click(self, **event_args):
    """Set rating to 4 stars"""
    self.star_click(4)

  def link_star_5_click(self, **event_args):
    """Set rating to 5 stars"""
    self.star_click(5)

  def button_submit_click(self, **event_args):
    """Submit review"""
    # Check if user is logged in
    user = anvil.users.get_user()

    if not user:
      alert("Please login to submit a review")
      return

    # Validate inputs
    if not self.txt_title.text or not self.txt_title.text.strip():
      alert("Please enter a title for your review")
      return

    if not self.txt_review.text or not self.txt_review.text.strip():
      alert("Please write your review")
      return

    # Submit review
    try:
      review_data = {
        'rating': self.rating,
        'title': self.txt_title.text.strip(),
        'comment': self.txt_review.text.strip()
      }

      result = anvil.server.call(
        'submit_review',
        self.item_type,
        self.item_id,
        review_data
      )

      if result['success']:
        Notification("Thank you! Your review has been submitted for approval.", 
                     style="success", 
                     timeout=5).show()

        # Close the form (if opened in alert dialog)
        self.raise_event('x-close-alert', value=True)

      else:
        alert(f"Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
      print(f"Error submitting review: {e}")
      alert(f"Failed to submit review: {str(e)}")