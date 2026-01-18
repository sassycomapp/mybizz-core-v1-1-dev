contact_serviceimport anvil.google.auth, anvil.google.drive, anvil.google.mail
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
from datetime import datetime, timedelta


## Function: get_all_contacts()

**Server:** server_customers/contact_service.py  
**Purpose:** Get all contacts with optional filtering  
**Returns:** {'success': bool, 'contacts': list} or {'success': False, 'error': str}

```python
@anvil.server.callable
def get_all_contacts(filters=None):
  """Get all contacts with optional filtering"""
  try:
    user = anvil.users.get_user()
    if not user:
      return {'success': False, 'error': 'Not authenticated'}

    # Base query
    query = {'instance_id': user}

    # Apply filters
    if filters:
      if filters.get('status'):
        query['status'] = filters['status']
      if filters.get('tags'):
        # Search for contacts with specific tags
        # TODO: Implement tag filtering
        pass
      if filters.get('search'):
        search_term = filters['search'].lower()
        # Search in name and email
        # TODO: Implement search logic
        pass

    contacts = app_tables.contacts.search(
      tables.order_by('last_contact_date', ascending=False),
      **query
    )

    # Convert to list with calculated fields
    contact_list = []
    for contact in contacts:
      contact_list.append({
        'contact_id': contact.get_id(),
        'first_name': contact['first_name'],
        'last_name': contact['last_name'],
        'full_name': f"{contact['first_name']} {contact['last_name']}",
        'email': contact['email'],
        'phone': contact['phone'],
        'status': contact['status'],
        'total_spent': contact['total_spent'] or 0,
        'total_transactions': contact['total_transactions'] or 0,
        'last_contact_date': contact['last_contact_date'],
        'customer_since': contact['date_added'],
        'source': contact['source'],
        'tags': contact['tags'] or [],
        'lifecycle_stage': contact['lifecycle_stage']
      })

    return {'success': True, 'contacts': contact_list}

  except Exception as e:
    print(f"Error getting contacts: {e}")
    return {'success': False, 'error': str(e)}
```

---

  ## Function: get_contact_by_id()

  **Server:** server_customers/contact_service.py  
  **Purpose:** Get single contact with full timeline  
  **Parameters:** contact_id (row ID from get_id())  
**Returns:** {'success': bool, 'contact': dict} or error

```python
@anvil.server.callable
def get_contact_by_id(contact_id):
  """Get single contact with full timeline"""
  try:
    user = anvil.users.get_user()
    if not user:
      return {'success': False, 'error': 'Not authenticated'}

    contact = app_tables.contacts.get_by_id(contact_id)
    if not contact or contact['instance_id'] != user:
      return {'success': False, 'error': 'Contact not found'}

    # Get contact events (timeline)
    events = app_tables.contact_events.search(
      contact_id=contact,
      user_visible=True,
      tables.order_by('event_date', ascending=False)
    )

    # Convert events to list
    event_list = []
    for event in events:
      event_list.append({
        'event_id': event.get_id(),
        'event_type': event['event_type'],
        'event_date': event['event_date'],
        'event_data': event['event_data'],
        'related_id': event['related_id']
      })

    # Build full contact object
    contact_data = {
      'contact_id': contact.get_id(),
      'first_name': contact['first_name'],
      'last_name': contact['last_name'],
      'email': contact['email'],
      'phone': contact['phone'],
      'status': contact['status'],
      'source': contact['source'],
      'date_added': contact['date_added'],
      'last_contact_date': contact['last_contact_date'],
      'total_spent': contact['total_spent'] or 0,
      'total_transactions': contact['total_transactions'] or 0,
      'average_order_value': contact['average_order_value'] or 0,
      'lifecycle_stage': contact['lifecycle_stage'],
      'tags': contact['tags'] or [],
      'internal_notes': contact['internal_notes'],
      'preferences': contact['preferences'] or {},
      'timeline': event_list
    }

    return {'success': True, 'contact': contact_data}

  except Exception as e:
    print(f"Error getting contact: {e}")
    return {'success': False, 'error': str(e)}
```

---

  ## Function: create_contact()

  **Server:** server_customers/contact_service.py  
  **Purpose:** Create new contact and initial timeline event  
**Parameters:** contact_data (dict with first_name, last_name, email, phone, source, tags, notes)  
**Returns:** {'success': bool, 'contact_id': row_id} or error

```python
@anvil.server.callable
def create_contact(contact_data):
  """Create new contact"""
  try:
    user = anvil.users.get_user()
    if not user:
      return {'success': False, 'error': 'Not authenticated'}

    # Validate required fields
    if not contact_data.get('email'):
      return {'success': False, 'error': 'Email is required'}

    # Check for duplicate
    existing = app_tables.contacts.get(
      instance_id=user,
      email=contact_data['email']
    )
    if existing:
      return {'success': False, 'error': 'Contact with this email already exists'}

    # Create contact
    contact = app_tables.contacts.add_row(
      instance_id=user,
      first_name=contact_data['first_name'],
      last_name=contact_data['last_name'],
      email=contact_data['email'],
      phone=contact_data.get('phone', ''),
      status='Lead',  # New contacts start as leads
      source=contact_data.get('source', 'Manual Entry'),
      date_added=datetime.now(),
      last_contact_date=datetime.now(),
      total_spent=0,
      total_transactions=0,
      average_order_value=0,
      lifecycle_stage='New',
      tags=contact_data.get('tags', []),
      internal_notes=contact_data.get('notes', ''),
      preferences={},
      created_at=datetime.now(),
      updated_at=datetime.now()
    )

    # Create initial event
    app_tables.contact_events.add_row(
      contact_id=contact,
      event_type='created',
      event_date=datetime.now(),
      event_data={'source': contact_data.get('source', 'Manual Entry')},
      related_id=None,
      user_visible=True
    )

    return {'success': True, 'contact_id': contact.get_id()}

  except Exception as e:
    print(f"Error creating contact: {e}")
    return {'success': False, 'error': str(e)}
```

---

  ## Function: update_contact()

  **Server:** server_customers/contact_service.py  
  **Purpose:** Update contact fields  
  **Parameters:** contact_id (row ID), updates (dict of fields to update)  
  **Returns:** {'success': bool, 'contact': dict} or error

  ```python
  @anvil.server.callable
  def update_contact(contact_id, updates):
"""Update contact information"""
try:
  user = anvil.users.get_user()
  if not user:
    return {'success': False, 'error': 'Not authenticated'}

  contact = app_tables.contacts.get_by_id(contact_id)
  if not contact or contact['instance_id'] != user:
    return {'success': False, 'error': 'Contact not found'}

    # Update allowed fields
  allowed_fields = ['first_name', 'last_name', 'phone', 'status', 'tags', 'internal_notes', 'preferences']

  for field, value in updates.items():
    if field in allowed_fields:
      contact[field] = value

  contact['updated_at'] = datetime.now()

  return {'success': True, 'contact': contact}

except Exception as e:
  print(f"Error updating contact: {e}")
  return {'success': False, 'error': str(e)}
```

---

  ## Function: delete_contact()

  **Server:** server_customers/contact_service.py  
**Purpose:** Soft delete contact (mark as Inactive)  
**Parameters:** contact_id (row ID)  
**Returns:** {'success': bool} or error

```python
@anvil.server.callable
def delete_contact(contact_id):
  """Soft delete contact (mark as inactive)"""
  try:
    user = anvil.users.get_user()
    if not user:
      return {'success': False, 'error': 'Not authenticated'}
    
    contact = app_tables.contacts.get_by_id(contact_id)
    if not contact or contact['instance_id'] != user:
      return {'success': False, 'error': 'Contact not found'}
    
    # Soft delete - mark as inactive
    contact['status'] = 'Inactive'
    contact['updated_at'] = datetime.now()
    
    # Log event
    app_tables.contact_events.add_row(
      contact_id=contact,
      event_type='deleted',
      event_date=datetime.now(),
      event_data={},
      related_id=None,
      user_visible=False
    )
    
    return {'success': True}
    
  except Exception as e:
    print(f"Error deleting contact: {e}")
    return {'success': False, 'error': str(e)}
```

---

## Function: add_note_to_contact()

**Server:** server_customers/contact_service.py  
**Purpose:** Add note to contact timeline  
**Parameters:** contact_id (row ID), note_text (string)  
**Returns:** {'success': bool, 'event_id': row_id} or error

```python
@anvil.server.callable
def add_note_to_contact(contact_id, note_text):
  """Add note to contact timeline"""
  try:
    user = anvil.users.get_user()
    if not user:
      return {'success': False, 'error': 'Not authenticated'}
    
    contact = app_tables.contacts.get_by_id(contact_id)
    if not contact or contact['instance_id'] != user:
      return {'success': False, 'error': 'Contact not found'}
    
    # Create note event
    event = app_tables.contact_events.add_row(
      contact_id=contact,
      event_type='note',
      event_date=datetime.now(),
      event_data={'note': note_text, 'author': user['email']},
      related_id=None,
      user_visible=True
    )
    
    # Update last contact date
    contact['last_contact_date'] = datetime.now()
    
    return {'success': True, 'event_id': event.get_id()}
    
  except Exception as e:
    print(f"Error adding note: {e}")
    return {'success': False, 'error': str(e)}
```

---

## Function: update_contact_from_transaction()

**Server:** server_customers/contact_service.py  
**Purpose:** Update contact when transaction occurs (booking/order)  
**Parameters:** email, transaction_type, transaction_id, amount  
**Returns:** {'success': bool, 'contact_id': row_id} or error

```python
@anvil.server.callable
def update_contact_from_transaction(email, transaction_type, transaction_id, amount):
  """Update contact from booking or order transaction"""
  try:
    user = anvil.users.get_user()
    if not user:
      return {'success': False, 'error': 'Not authenticated'}
    
    # Get or create contact
    contact = app_tables.contacts.get(
      instance_id=user,
      email=email
    )
    
    if not contact:
      # Create new contact from transaction
      contact = app_tables.contacts.add_row(
        instance_id=user,
        email=email,
        first_name='',
        last_name='',
        phone='',
        status='Customer',
        source=f'{transaction_type}_widget',
        date_added=datetime.now(),
        last_contact_date=datetime.now(),
        total_spent=0,
        total_transactions=0,
        average_order_value=0,
        lifecycle_stage='New',
        tags=[],
        internal_notes='',
        preferences={},
        created_at=datetime.now(),
        updated_at=datetime.now()
      )
    
    # Update metrics
    contact['total_spent'] = (contact['total_spent'] or 0) + amount
    contact['total_transactions'] = (contact['total_transactions'] or 0) + 1
    contact['average_order_value'] = contact['total_spent'] / contact['total_transactions']
    contact['last_contact_date'] = datetime.now()
    contact['status'] = 'Customer'
    
    # Log event
    app_tables.contact_events.add_row(
      contact_id=contact,
      event_type=transaction_type,
      event_date=datetime.now(),
      event_data={'amount': amount},
      related_id=str(transaction_id),
      user_visible=True
    )
    
    return {'success': True, 'contact_id': contact.get_id()}
    
  except Exception as e:
    print(f"Error updating contact from transaction: {e}")
    return {'success': False, 'error': str(e)}
```

