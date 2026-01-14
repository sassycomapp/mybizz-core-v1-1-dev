from ._anvil_designer import TicketManagementFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class TicketManagementForm(TicketManagementFormTemplate):
  """Ticket management dashboard for staff"""

  def __init__(self, **properties):
    self.init_components(**properties)

    # Check permissions
    user = anvil.users.get_user()
    if not user or user['role'] not in ['owner', 'manager', 'staff']:
      alert("Access denied")
      open_form('dashboard.DashboardForm')
      return

    # Configure title
    self.lbl_title.text = "Ticket Management"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True

    # Configure status filter
    self.dd_status_filter.items = [
      ('All Statuses', None),
      ('Open', 'open'),
      ('In Progress', 'in_progress'),
      ('Resolved', 'resolved'),
      ('Closed', 'closed')
    ]
    self.dd_status_filter.selected_value = None

    # Configure priority filter
    self.dd_priority_filter.items = [
      ('All Priorities', None),
      ('Urgent', 'urgent'),
      ('High', 'high'),
      ('Medium', 'medium'),
      ('Low', 'low')
    ]
    self.dd_priority_filter.selected_value = None

    # Configure assigned filter
    self.dd_assigned_filter.items = [
      ('All Staff', None),
      ('Unassigned', 'unassigned'),
      ('Assigned to Me', 'me')
    ]
    self.dd_assigned_filter.selected_value = None

    # Configure data grid
    self.dg_tickets.columns = [
      {'id': 'number', 'title': 'Ticket #', 'data_key': 'ticket_number', 'width': 120},
      {'id': 'customer', 'title': 'Customer', 'data_key': 'customer_display', 'width': 150},
      {'id': 'subject', 'title': 'Subject', 'data_key': 'subject', 'width': 250},
      {'id': 'status', 'title': 'Status', 'data_key': 'status_display', 'width': 120},
      {'id': 'priority', 'title': 'Priority', 'data_key': 'priority_display', 'width': 100},
      {'id': 'date', 'title': 'Created', 'data_key': 'date_display', 'width': 120},
      {'id': 'actions', 'title': 'Actions', 'data_key': None, 'width': 100}
    ]

    # Load tickets
    self.load_tickets()

  def load_tickets(self):
    """Load tickets with filters"""
    try:
      filters = {
        'status': self.dd_status_filter.selected_value,
        'priority': self.dd_priority_filter.selected_value,
        'assigned': self.dd_assigned_filter.selected_value
      }

      result = anvil.server.call('get_all_tickets', filters)

      if result['success']:
        tickets = result['data']

        # Format display fields
        for ticket in tickets:
          # Customer display
          if ticket.get('customer_id'):
            ticket['customer_display'] = ticket['customer_id']['email']
          else:
            ticket['customer_display'] = ticket.get('customer_name', 'Guest')

          # Status display with emoji
          status_emoji = {
            'open': '🔓',
            'in_progress': '⏳',
            'resolved': '✅',
            'closed': '🔒'
          }
          status = ticket.get('status', 'open')
          ticket['status_display'] = f"{status_emoji.get(status, '')} {status.replace('_', ' ').title()}"

          # Priority display
          priority = ticket.get('priority', 'medium')
          ticket['priority_display'] = priority.title()

          # Date display
          created_at = ticket.get('created_at')
          if created_at:
            ticket['date_display'] = created_at.strftime('%d %b %Y')
          else:
            ticket['date_display'] = 'Unknown'

        self.dg_tickets.items = tickets

      else:
        alert(f"Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
      print(f"Error loading tickets: {e}")
      alert(f"Failed to load tickets: {str(e)}")

  def dropdown_status_filter_change(self, **event_args):
    """Reload when status filter changes"""
    self.load_tickets()

  def dropdown_priority_filter_change(self, **event_args):
    """Reload when priority filter changes"""
    self.load_tickets()

  def dropdown_assigned_filter_change(self, **event_args):
    """Reload when assigned filter changes"""
    self.load_tickets()

  @handle("dd_status_filter", "change")
  def dd_status_filter_change(self, **event_args):
    """This method is called when an item is selected"""
    pass

  @handle("dd_priority_filter", "change")
  def dd_priority_filter_change(self, **event_args):
    """This method is called when an item is selected"""
    pass

  @handle("dd_assigned_filer", "change")
  def dd_assigned_filer_change(self, **event_args):
    """This method is called when an item is selected"""
    pass
