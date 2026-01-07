from ._anvil_designer import TicketItemTemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class TicketItemTemplate(TicketItemTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    # Status emoji
    status_emoji = {
      'open': '🟢',
      'in_progress': '🔵',
      'resolved': '✅',
      'closed': '⚪'
    }

    emoji = status_emoji.get(self.item['status'], '⚪')
    status_text = self.item['status'].replace('_', ' ').title()

    # Header
    self.lbl_ticket_header.text = f"{self.item['ticket_number']}  •  {self.item['subject']}  {emoji} {status_text}"
    self.lbl_ticket_header.bold = True
    self.lbl_ticket_header.font_size = 14

    # Meta
    created = self.item['created_at'].strftime('%b %d, %Y')
    updated = self.item['updated_at'].strftime('%b %d, %Y') if self.item.get('updated_at') else created

    self.lbl_ticket_meta.text = f"Created: {created}  •  Last updated: {updated}"
    self.lbl_ticket_meta.font_size = 12
    self.lbl_ticket_meta.foreground = "#666666"

    # View link
    self.link_view.text = "View Thread"
    self.link_view.role = "secondary-color"

  def link_view_click(self, **event_args):
    """View ticket thread"""
    result = alert(
      content=TicketThreadModal(ticket_id=self.item.get_id()),
      title=self.item['ticket_number'],
      large=True,
      buttons=[("Close", None)]
    )