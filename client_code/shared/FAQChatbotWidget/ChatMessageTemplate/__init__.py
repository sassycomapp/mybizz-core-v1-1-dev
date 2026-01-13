from ._anvil_designer import ChatMessageTemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ChatMessageTemplate(ChatMessageTemplateTemplate):
  """Chat message row"""

  def __init__(self, **properties):
    self.message = self.item
    self.init_components(**properties)

    msg_type = self.message['type']

    if msg_type == 'bot':
      # Bot message (left-aligned)
      self.lbl_message.text = f"🤖 {self.message['text']}"
      self.lbl_message.background = "#E3F2FD"
      self.lbl_message.foreground = "#000000"
      self.lbl_message.bold = False
      self.lbl_message.align = "left"

      # Show articles if any
      if self.message.get('articles'):
        for article in self.message['articles']:
          link = Link(
            text=f"• {article['title']}",
            url=article['url'],
            foreground="#2196F3",
            spacing_above='small'
          )
          self.col_articles.add_component(link)
      else:
        self.col_articles.visible = False

    else:
      # User message (right-aligned)
      self.lbl_message.text = self.message['text']
      self.lbl_message.background = "#4CAF50"
      self.lbl_message.foreground = "white"
      self.lbl_message.bold = False
      self.lbl_message.align = "right"
      self.col_articles.visible = False