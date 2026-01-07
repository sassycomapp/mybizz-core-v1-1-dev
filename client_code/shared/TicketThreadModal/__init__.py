from ._anvil_designer import TicketThreadModalTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class TicketThreadModal(TicketThreadModalTemplate):
  def __init__(self, ticket_id=None, **properties):
    self.ticket_id = ticket_id
    self.init_components(**properties)

    # Configure message input
    self.txt_message.placeholder = "Type your message here..."
    self.txt_message.rows = 3

    # Configure send button
    self.btn_send.text = "Send Message"
    self.btn_send.icon = "fa:paper-plane"
    self.btn_send.role = "primary-color"

    # Set repeating panel template
    self.rp_messages.item_template = 'shared.TicketMessageTemplate'

    # Load messages
    self.load_messages()

  def load_messages(self):
    """Load ticket messages"""
    try:
      messages = anvil.server.call('get_ticket_messages', self.ticket_id)
      self.rp_messages.items = messages
    except Exception as e:
      alert(f"Error loading messages: {str(e)}")

  def button_send_click(self, **event_args):
    """Send message"""
    if not self.txt_message.text:
      return

    try:
      result = anvil.server.call('add_ticket_message', self.ticket_id, self.txt_message.text)

      if result['success']:
        self.txt_message.text = ""
        self.load_messages()
      else:
        alert(result['error'])

    except Exception as e:
      alert(f"Error sending message: {str(e)}")