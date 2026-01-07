from ._anvil_designer import GuestbookFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class GuestbookForm(GuestbookFormTemplate):
  def __init__(self, **properties):
    self.selected_rating = 5
    self.init_components(**properties)

    # Configure back link
    self.link_back.text = "← Back to Home"
    self.link_back.role = "secondary-color"

    # Configure title
    self.lbl_title.text = "Guestbook"
    self.lbl_title.font_size = 28
    self.lbl_title.bold = True
    self.lbl_title.align = "center"
    self.lbl_title.role = "headline"

    # Configure subtitle
    self.lbl_subtitle.text = "Share your experience with us!"
    self.lbl_subtitle.font_size = 16
    self.lbl_subtitle.align = "center"
    self.lbl_subtitle.foreground = "#666666"

    # Configure repeating panel
    self.rp_entries.item_template = 'bookings.GuestbookEntryTemplate'

    # Configure no entries label
    self.lbl_no_entries.text = "No reviews yet. Be the first to share your experience!"
    self.lbl_no_entries.align = "center"
    self.lbl_no_entries.foreground = "#666666"
    self.lbl_no_entries.visible = False

    # Configure review section
    self.lbl_review_section.text = "LEAVE A REVIEW"
    self.lbl_review_section.bold = True
    self.lbl_review_section.font_size = 18

    # Configure input fields
    self.txt_guest_name.placeholder = "Your name"
    self.txt_guest_name.icon = "fa:user"

    self.txt_email.placeholder = "your@email.com"
    self.txt_email.type = "email"
    self.txt_email.icon = "fa:envelope"

    # Create star rating
    self.create_star_rating()

    self.txt_review.placeholder = "Share your experience..."
    self.txt_review.rows = 5

    # Configure submit button
    self.btn_submit.text = "Submit Review"
    self.btn_submit.icon = "fa:paper-plane"
    self.btn_submit.role = "primary-color"

    # Configure message label
    self.lbl_message.visible = False
    self.lbl_message.align = "center"

    # Load entries
    self.load_entries()

  def create_star_rating(self):
    """Create interactive star rating"""
    self.col_rating.clear()

    rating_label = Label(text="Rating:", bold=True)
    self.col_rating.add_component(rating_label)

    star_panel = FlowPanel()

    for i in range(1, 6):
      star = Label(
        text="★",
        font_size=32,
        foreground="#FFD700" if i <= self.selected_rating else "#CCCCCC"
      )
      star.tag = i
      star.set_event_handler('mouse_enter', self.star_hover)
      star.set_event_handler('mouse_leave', self.star_unhover)
      star.set_event_handler('click', self.star_click)
      star_panel.add_component(star)

    self.col_rating.add_component(star_panel)

  def star_hover(self, sender, **event_args):
    """Highlight stars on hover"""
    rating = sender.tag
    for star in sender.parent.get_components():
      if hasattr(star, 'tag') and star.tag <= rating:
        star.foreground = "#FFD700"
      else:
        star.foreground = "#CCCCCC"

  def star_unhover(self, sender, **event_args):
    """Reset stars to selected rating"""
    self.update_star_display()

  def star_click(self, sender, **event_args):
    """Set rating"""
    self.selected_rating = sender.tag
    self.update_star_display()

  def update_star_display(self):
    """Update star colors based on selected rating"""
    for star in self.col_rating.get_components()[1].get_components():
      if hasattr(star, 'tag'):
        if star.tag <= self.selected_rating:
          star.foreground = "#FFD700"
        else:
          star.foreground = "#CCCCCC"

  def load_entries(self):
    """Load approved guestbook entries"""
    try:
      entries = anvil.server.call('get_public_guestbook_entries')

      if entries:
        self.rp_entries.items = entries
        self.rp_entries.visible = True
        self.lbl_no_entries.visible = False
      else:
        self.rp_entries.visible = False
        self.lbl_no_entries.visible = True

    except Exception as e:
      print(f"Error loading entries: {e}")

  def button_submit_click(self, **event_args):
    """Submit guestbook entry"""
    try:
      self.lbl_message.visible = False

      # Validate
      if not self.txt_guest_name.text:
        self.show_message("Name is required", "warning")
        return

      if not self.txt_email.text:
        self.show_message("Email is required", "warning")
        return

      if not self.txt_review.text or len(self.txt_review.text) < 10:
        self.show_message("Please write at least 10 characters", "warning")
        return

      # Submit entry
      entry_data = {
        'guest_name': self.txt_guest_name.text,
        'guest_email': self.txt_email.text,
        'rating': self.selected_rating,
        'comment': self.txt_review.text
      }

      result = anvil.server.call('submit_guestbook_entry', entry_data)

      if result['success']:
        self.show_message(
          "✅ Thank you for your review! It will appear after approval.",
          "success"
        )
        # Clear form
        self.txt_guest_name.text = ""
        self.txt_email.text = ""
        self.txt_review.text = ""
        self.selected_rating = 5
        self.update_star_display()
      else:
        self.show_message(result['error'], "danger")

    except Exception as e:
      self.show_message(f"Error submitting review: {str(e)}", "danger")

  @handle("link_back", "click")
  def link_back_click(self, **event_args):
    """Navigate back to home"""
    open_form('HomePage')  # Or whatever your home form is

  def show_message(self, text, style):
    """Display message"""
    self.lbl_message.text = text
    self.lbl_message.role = f"alert-{style}"
    self.lbl_message.visible = True

  @handle("btn_submit", "click")
  def btn_submit_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
