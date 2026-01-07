from ._anvil_designer import ClientNoteTemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ClientNoteTemplate(ClientNoteTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    # Display timestamp
    timestamp = self.item['created_at'].strftime('%b %d, %Y - %I:%M %p')
    self.lbl_timestamp.text = timestamp
    self.lbl_timestamp.font_size = 12
    self.lbl_timestamp.foreground = "#666666"

    # Display author
    author_name = "Unknown"
    if self.item.get('created_by'):
      author_name = self.item['created_by']['email'].split('@')[0]
    self.lbl_author.text = author_name
    self.lbl_author.bold = True
    self.lbl_author.font_size = 14

    # Display note
    self.lbl_note.text = self.item['note']
    self.lbl_note.foreground = "#333333"

    # Confidential badge
    if self.item.get('is_confidential', False):
      self.lbl_confidential.text = "🔒 CONFIDENTIAL"
      self.lbl_confidential.visible = True
      self.lbl_confidential.background = "#FFC107"
      self.lbl_confidential.foreground = "#000000"
      self.lbl_confidential.bold = True
      self.lbl_confidential.font_size = 10
    else:
      self.lbl_confidential.visible = False