from ._anvil_designer import MyTicketsFormTemplate
from anvil import *
from routing import router
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class MyTicketsForm(MyTicketsFormTemplate):
  def __init__(self, **properties):
    self.current_user = None
    self.init_components(**properties)

    # Check if logged in
    user = anvil.users.get_user()
    if not user:
      open_form('auth.LoginForm')
      return

    self.current_user = user

    # Configure title
    self.lbl_title.text = "My Support Tickets"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True
    self.lbl_title.role = "headline"

    # Configure new ticket button
    self.btn_new_ticket.text = "New Ticket"
    self.btn_new_ticket.icon = "fa:plus"
    self.btn_new_ticket.role = "primary-color"

    # Configure status filter
    self.dd_status_filter.items = [
      ('All Statuses', 'all'),
      ('Open', 'open'),
      ('In Progress', 'in_progress'),
      ('Resolved', 'resolved'),
      ('Closed', 'closed')
    ]
    self.dd_status_filter.selected_value = 'all'

    # Configure no tickets label
    self.lbl_no_tickets.text = "No tickets yet. Click 'New Ticket' to create one!"
    self.lbl_no_tickets.align = "center"
    self.lbl_no_tickets.foreground = "#666666"
    self.lbl_no_tickets.visible = False

    # Set repeating panel template
    self.rp_tickets.item_template = 'shared.TicketItemTemplate'

    # Load tickets
    self.load_tickets()

  def load_tickets(self):
    """Load customer's tickets"""
    try:
      status_filter = self.dd_status_filter.selected_value
      tickets = anvil.server.call('get_my_tickets', status_filter)

      if tickets:
        self.rp_tickets.items = tickets
        self.rp_tickets.visible = True
        self.lbl_no_tickets.visible = False
      else:
        self.rp_tickets.visible = False
        self.lbl_no_tickets.visible = True

    except Exception as e:
      alert(f"Error loading tickets: {str(e)}")

  def button_new_ticket_click(self, **event_args):
    """Create new ticket"""
    result = alert(
      content=NewTicketModal(),
      title="Create Support Ticket",
      large=True,
      buttons=[("Cancel", False), ("Submit", True)]
    )

    if result:
      self.load_tickets()

  def dropdown_status_filter_change(self, **event_args):
    """Filter tickets by status"""
    self.load_tickets()

  @handle("btn_new_ticket", "click")
  def btn_new_ticket_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("dd_status_filter", "change")
  def dd_status_filter_change(self, **event_args):
    """This method is called when an item is selected"""
    pass
