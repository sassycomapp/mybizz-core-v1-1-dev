import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.stripe
import anvil.secrets
import anvil.files
from anvil.files import data_files
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
@anvil.users.login_required
def get_ticket(ticket_id):
  """
  Get ticket details and messages.
  
  Args:
    ticket_id (str): Ticket ID
    
  Returns:
    dict: {'success': bool, 'data': dict} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager', 'staff']:
      return {'success': False, 'error': 'Access denied'}

    # Get ticket
    ticket = app_tables.support_tickets.get_by_id(ticket_id)

    if not ticket:
      return {'success': False, 'error': 'Ticket not found'}

    # Add customer display name
    customer = ticket.get('customer_id')
    if customer:
      ticket['customer_display'] = customer.get('email', 'Guest')
    else:
      ticket['customer_display'] = ticket.get('customer_email', 'Guest')

    # Get messages
    messages = list(app_tables.ticket_messages.search(
      ticket_id=ticket,
      tables.order_by('created_at')
    ))

    return {
      'success': True,
      'data': {
        'ticket': ticket,
        'messages': messages
      }
    }

  except Exception as e:
    print(f"Error getting ticket: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
@anvil.users.login_required
def get_staff_users():
  """
  Get all staff users for assignment.
  
  Returns:
    dict: {'success': bool, 'data': list} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager', 'staff']:
      return {'success': False, 'error': 'Access denied'}

    # Get staff users
    staff = list(app_tables.users.search(
      role=q.any_of('owner', 'manager', 'staff')
    ))

    return {'success': True, 'data': staff}

  except Exception as e:
    print(f"Error getting staff: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
@anvil.users.login_required
def update_ticket_priority(ticket_id, priority):
  """
  Update ticket priority.
  
  Args:
    ticket_id (str): Ticket ID
    priority (str): New priority
    
  Returns:
    dict: {'success': bool} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager', 'staff']:
      return {'success': False, 'error': 'Access denied'}

    ticket = app_tables.support_tickets.get_by_id(ticket_id)

    if not ticket:
      return {'success': False, 'error': 'Ticket not found'}

    ticket['priority'] = priority
    ticket['updated_at'] = datetime.now()
    ticket.update()

    return {'success': True}

  except Exception as e:
    print(f"Error updating priority: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
@anvil.users.login_required
def update_ticket_status(ticket_id, status):
  """
  Update ticket status.
  
  Args:
    ticket_id (str): Ticket ID
    status (str): New status
    
  Returns:
    dict: {'success': bool} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager', 'staff']:
      return {'success': False, 'error': 'Access denied'}

    ticket = app_tables.support_tickets.get_by_id(ticket_id)

    if not ticket:
      return {'success': False, 'error': 'Ticket not found'}

    old_status = ticket['status']
    ticket['status'] = status
    ticket['updated_at'] = datetime.now()

    # If closing or resolving, set closed/resolved timestamp
    if status in ['resolved', 'closed'] and old_status not in ['resolved', 'closed']:
      ticket['resolved_at'] = datetime.now()

    ticket.update()

    return {'success': True}

  except Exception as e:
    print(f"Error updating status: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
@anvil.users.login_required
def assign_ticket(ticket_id, staff_id):
  """
  Assign ticket to staff member.
  
  Args:
    ticket_id (str): Ticket ID
    staff_id (str): Staff user ID (None to unassign)
    
  Returns:
    dict: {'success': bool} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager', 'staff']:
      return {'success': False, 'error': 'Access denied'}

    ticket = app_tables.support_tickets.get_by_id(ticket_id)

    if not ticket:
      return {'success': False, 'error': 'Ticket not found'}

    if staff_id:
      staff_user = app_tables.users.get_by_id(staff_id)
      if not staff_user:
        return {'success': False, 'error': 'Staff member not found'}
      ticket['assigned_to'] = staff_user
    else:
      ticket['assigned_to'] = None

    ticket['updated_at'] = datetime.now()
    ticket.update()

    return {'success': True}

  except Exception as e:
    print(f"Error assigning ticket: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
@anvil.users.login_required
def add_ticket_message(ticket_id, message, is_internal_note=False):
  """
  Add message to ticket.
  
  Args:
    ticket_id (str): Ticket ID
    message (str): Message text
    is_internal_note (bool): Internal staff note?
    
  Returns:
    dict: {'success': bool} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager', 'staff']:
      return {'success': False, 'error': 'Access denied'}

    ticket = app_tables.support_tickets.get_by_id(ticket_id)

    if not ticket:
      return {'success': False, 'error': 'Ticket not found'}

    # Create message
    app_tables.ticket_messages.add_row(
      ticket_id=ticket,
      author_id=user,
      author_type='staff',
      message=message,
      is_internal_note=is_internal_note,
      created_at=datetime.now()
    )

    # Update ticket
    ticket['updated_at'] = datetime.now()
    ticket['last_reply_at'] = datetime.now()

    # If status is closed, reopen to in_progress
    if ticket['status'] == 'closed':
      ticket['status'] = 'in_progress'

    ticket.update()

    # Send email notification to customer (if not internal note)
    if not is_internal_note:
      # TODO: Implement email notification
      pass

    return {'success': True}

  except Exception as e:
    print(f"Error adding message: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
@anvil.users.login_required
def get_all_tickets(filters):
  """
  Get all tickets with optional filters.
  
  Args:
    filters (dict): {'status': str, 'priority': str, 'assigned': str}
    
  Returns:
    dict: {'success': bool, 'data': list} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager', 'staff']:
      return {'success': False, 'error': 'Access denied'}

    # Build query
    query = {}

    # Apply status filter
    if filters.get('status'):
      query['status'] = filters['status']

    # Apply priority filter
    if filters.get('priority'):
      query['priority'] = filters['priority']

    # Query tickets
    tickets = list(app_tables.support_tickets.search(**query))

    # Apply assigned filter
    if filters.get('assigned') == 'unassigned':
      tickets = [t for t in tickets if not t.get('assigned_to')]
    elif filters.get('assigned') == 'me':
      tickets = [t for t in tickets if t.get('assigned_to') == user]

    # Sort by priority (urgent first) then date (newest first)
    priority_order = {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}
    tickets.sort(
      key=lambda t: (
        priority_order.get(t.get('priority', 'medium'), 2),
        -(t.get('created_at').timestamp() if t.get('created_at') else 0)
      )
    )

    return {'success': True, 'data': tickets}

  except Exception as e:
    print(f"Error getting tickets: {e}")
    return {'success': False, 'error': str(e)}

from datetime import datetime
import random

def generate_ticket_number():
  """
  Generate unique ticket number.
  
  Returns:
    str: Ticket number (e.g. TKT-20260114-3847)
  """
  timestamp = datetime.now().strftime('%Y%m%d')
  random_num = random.randint(1000, 9999)
  return f"TKT-{timestamp}-{random_num}"


@anvil.server.callable
def create_ticket(customer_data, ticket_data):
  """
  Create new support ticket.
  
  Args:
    customer_data (dict): {'name': str, 'email': str} for guest users, None for logged-in
    ticket_data (dict): {'subject': str, 'category': str, 'description': str, 'attachments': list}
    
  Returns:
    dict: {'success': bool, 'ticket_number': str} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    # Generate unique ticket number
    ticket_number = generate_ticket_number()

    # Get customer info
    if user:
      customer_id = user
      customer_name = user.get('name') or user['email'].split('@')[0]
      customer_email = user['email']
    else:
      customer_id = None
      customer_name = customer_data['name']
      customer_email = customer_data['email']

    # Create ticket
    ticket = app_tables.support_tickets.add_row(
      ticket_number=ticket_number,
      customer_id=customer_id,
      customer_name=customer_name if not user else None,
      customer_email=customer_email,
      subject=ticket_data['subject'],
      category=ticket_data['category'],
      status='open',
      priority='medium',
      assigned_to=None,
      created_at=datetime.now(),
      updated_at=datetime.now()
    )

    # Add initial message with description
    app_tables.ticket_messages.add_row(
      ticket_id=ticket,
      author_id=customer_id,
      author_type='customer',
      message=ticket_data['description'],
      is_internal_note=False,
      attachments=ticket_data.get('attachments'),
      created_at=datetime.now()
    )

    # TODO: Send confirmation email
    # send_ticket_confirmation_email(customer_email, ticket_number)

    # TODO: Notify staff of new ticket
    # notify_staff_new_ticket(ticket)

    return {
      'success': True,
      'ticket_number': ticket_number
    }

  except Exception as e:
    print(f"Error creating ticket: {e}")
    return {
      'success': False,
      'error': str(e)
    }