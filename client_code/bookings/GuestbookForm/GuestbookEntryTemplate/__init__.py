from ._anvil_designer import GuestbookEntryTemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class GuestbookEntryTemplate(GuestbookEntryTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    # Display stars
    rating = self.item['rating']
    filled_stars = "★" * rating
    empty_stars = "☆" * (5 - rating)
    self.lbl_stars.text = filled_stars + empty_stars
    self.lbl_stars.foreground = "#FFD700"
    self.lbl_stars.font_size = 20

    # Display title (first line of comment or "Great experience!")
    comment_lines = self.item['comment'].split('\n')
    title = comment_lines[0][:50] if comment_lines[0] else "Great experience!"
    self.lbl_title.text = f'"{title}"'
    self.lbl_title.bold = True
    self.lbl_title.font_size = 16

    # Display comment
    self.lbl_comment.text = self.item['comment']
    self.lbl_comment.foreground = "#333333"

    # Display meta (guest name and date)
    guest_name = self.item.get('guest_name', 'Anonymous')
    date = self.item['created_at'].strftime('%b %Y')
    self.lbl_meta.text = f"- {guest_name}, {date}"
    self.lbl_meta.font_size = 12
    self.lbl_meta.foreground = "#999999"
    self.lbl_meta.italic = True