from ._anvil_designer import TicketDetailFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class TicketDetailForm(TicketDetailFormTemplate):
  """Ticket detail view with conversation thread"""

  def __init__(self, ticket_id=None, **properties):
    self.ticket_id = ticket_id
    self.ticket = None
    self.init_components(**properties)

    # Check permissions
    user = anvil.users.get_user()
    if not user or user['role'] not in ['owner', 'manager', 'staff']:
      alert("Access denied")
      open_form('dashboard.DashboardForm')
      return

    # Configure button
    self.btn_send_reply.text = "Send Reply"
    self.btn_send_reply.icon = "fa:paper-plane"
    self.btn_send_reply.role = "primary-color"

    # Configure internal note checkbox
    self.cb_internal_note.text = "Internal Note (staff only)"

    # Configure reply textarea
    self.txt_reply.placeholder = "Type your reply..."
    self.txt_reply.rows = 3

    # Load ticket
    if ticket_id:
      self.load_ticket()

  def load_ticket(self):
    """Load ticket details and messages"""
    try:
      result = anvil.server.call('get_ticket', self.ticket_id)

      if result['success']:
        self.ticket = result['data']['ticket']
        messages = result['data']['messages']

        # Display ticket header
        self.lbl_ticket_number.text = f"Ticket {self.ticket['ticket_number']}"
        self.lbl_ticket_number.font_size = 20
        self.lbl_ticket_number.bold = True

        self.lbl_subject.text = f"Subject: {self.ticket['subject']}"
        self.lbl_subject.font_size = 16

        customer = self.ticket.get('customer_display', 'Guest')
        self.lbl_customer.text = f"Customer: {customer}"
        self.lbl_customer.font_size = 14
        self.lbl_customer.foreground = "#666666"

        # Priority dropdown
        self.dd_priority.items = [
          ('Low', 'low'),
          ('Medium', 'medium'),
          ('High', 'high'),
          ('Urgent', 'urgent')
        ]
        self.dd_priority.selected_value = self.ticket.get('priority', 'medium')

        # Status dropdown
        self.dd_status.items = [
          ('Open', 'open'),
          ('In Progress', 'in_progress'),
          ('Resolved', 'resolved'),
          ('Closed', 'closed')
        ]
        self.dd_status.selected_value = self.ticket.get('status', 'open')

        # Load staff for assignment
        self.load_staff_list()

        # Load messages
        self.rp_messages.items = messages

      else:
        alert(f"Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
      print(f"Error loading ticket: {e}")
      alert(f"Failed to load ticket: {str(e)}")

  def load_staff_list(self):
    """Load staff members for assignment dropdown"""
    try:
      result = anvil.server.call('get_staff_users')

      if result['success']:
        staff = result['data']
        items = [('Unassigned', None)]
        items.extend([(s['email'], s.get_id()) for s in staff])

        self.dd_assigned.items = items

        # Set current assignment
        if self.ticket.get('assigned_to'):
          self.dd_assigned.selected_value = self.ticket['assigned_to'].get_id()
        else:
          self.dd_assigned.selected_value = None

      else:
        print(f"Error loading staff: {result.get('error')}")

    except Exception as e:
      print(f"Error loading staff: {e}")

  def dropdown_priority_change(self, **event_args):
    """Update ticket priority"""
    new_priority = self.dd_priority.selected_value

    try:
      result = anvil.server.call('update_ticket_priority', self.ticket_id, new_priority)

      if result['success']:
        Notification("Priority updated", style="success").show()
      else:
        alert(f"Error: {result.get('error')}")

    except Exception as e:
      print(f"Error updating priority: {e}")
      alert(f"Failed to update priority: {str(e)}")

  def dropdown_status_change(self, **event_args):
    """Update ticket status"""
    new_status = self.dd_status.selected_value

    try:
      result = anvil.server.call('update_ticket_status', self.ticket_id, new_status)

      if result['success']:
        Notification("Status updated", style="success").show()

        # Reload to show any automated changes
        self.load_ticket()
      else:
        alert(f"Error: {result.get('error')}")

    except Exception as e:
      print(f"Error updating status: {e}")
      alert(f"Failed to update status: {str(e)}")

  def dropdown_assigned_change(self, **event_args):
    """Assign ticket to staff member"""
    staff_id = self.dd_assigned.selected_value

    try:
      result = anvil.server.call('assign_ticket', self.ticket_id, staff_id)

      if result['success']:
        Notification("Ticket assigned", style="success").show()
      else:
        alert(f"Error: {result.get('error')}")

    except Exception as e:
      print(f"Error assigning ticket: {e}")
      alert(f"Failed to assign ticket: {str(e)}")

  def button_send_reply_click(self, **event_args):
    """Send reply to ticket"""
    if not self.txt_reply.text or not self.txt_reply.text.strip():
      alert("Please enter a reply")
      return

    try:
      is_internal = self.cb_internal_note.checked

      result = anvil.server.call(
        'add_ticket_message',
        self.ticket_id,
        self.txt_reply.text.strip(),
        is_internal
      )

      if result['success']:
        Notification("Reply sent!", style="success").show()

        # Clear form
        self.txt_reply.text = ''
        self.cb_internal_note.checked = False

        # Reload messages
        self.load_ticket()

      else:
        alert(f"Error: {result.get('error')}")

    except Exception as e:
      print(f"Error sending reply: {e}")
      alert(f"Failed to send reply: {str(e)}")

  @handle("dd_priority", "change")
  def dd_priority_change(self, **event_args):
    """This method is called when an item is selected"""
    pass

  @handle("dd_status", "change")
  def dd_status_change(self, **event_args):
    """This method is called when an item is selected"""
    pass

  @handle("dd_assigned", "change")
  def dd_assigned_change(self, **event_args):
    """This method is called when an item is selected"""
    pass

  @handle("btn_send_reply", "click")
  def btn_send_reply_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
