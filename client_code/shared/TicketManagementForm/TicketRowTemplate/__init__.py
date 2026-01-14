from ._anvil_designer import TicketRowTemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables



class TicketRowTemplate(TicketRowTemplateTemplate):
  """Ticket row in data grid"""

  def __init__(self, **properties):
    self.ticket = self.item
    self.init_components(**properties)

    # Display ticket data
    self.lbl_ticket_number.text = self.ticket.get('ticket_number', 'N/A')
    self.lbl_customer.text = self.ticket.get('customer_display', 'Unknown')
    self.lbl_subject.text = self.ticket.get('subject', 'No subject')
    self.lbl_status.text = self.ticket.get('status_display', 'Unknown')
    self.lbl_priority.text = self.ticket.get('priority_display', 'Medium')
    self.lbl_date.text = self.ticket.get('date_display', 'N/A')

    # Configure view button
    self.btn_view.text = "View"
    self.btn_view.icon = "fa:eye"
    self.btn_view.role = "outlined-button"

  def button_view_click(self, **event_args):
    """Open ticket detail form"""
    from ..shared.TicketDetailForm import TicketDetailForm

    ticket_detail = TicketDetailForm(ticket_id=self.ticket.get_id())

    result = alert(
      ticket_detail,
      large=True,
      title=f"Ticket {self.ticket.get('ticket_number', 'Detail')}"
    )

    # Refresh list after closing detail
    if result:
      self.parent.parent.parent.load_tickets()  # Call parent form's load_tickets

  @handle("btn_view", "click")
  def btn_view_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
