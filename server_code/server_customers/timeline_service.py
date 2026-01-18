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

# MODULE 3: server_customers/timeline_service.py

**Purpose:** Contact activity timeline management

**Module Imports:**
  ```python
    import anvil.server
  import anvil.users
import anvil.tables as tables
from anvil.tables import app_tables
from datetime import datetime
```

---

  ## Function: get_contact_timeline()

  **Server:** server_customers/timeline_service.py  
  **Purpose:** Get chronological activity for contact  
  **Parameters:** contact_id (row ID)  
  **Returns:** {'success': bool, 'timeline': list} or error

```python
@anvil.server.callable
def get_contact_timeline(contact_id):
  """Get contact activity timeline"""
  try:
    user = anvil.users.get_user()
    if not user:
      return {'success': False, 'error': 'Not authenticated'}

    contact = app_tables.contacts.get_by_id(contact_id)
    if not contact or contact['instance_id'] != user:
      return {'success': False, 'error': 'Contact not found'}

    events = app_tables.contact_events.search(
      contact_id=contact,
      user_visible=True,
      tables.order_by('event_date', ascending=False)
    )

    timeline = []
    for event in events:
      timeline.append({
        'event_type': event['event_type'],
        'event_date': event['event_date'],
        'event_data': event['event_data'],
        'related_id': event['related_id']
      })

    return {'success': True, 'timeline': timeline}

  except Exception as e:
    print(f"Error getting timeline: {e}")
    return {'success': False, 'error': str(e)}
```

---

  ## Function: log_contact_event()

  **Server:** server_customers/timeline_service.py  
  **Purpose:** Log new event to contact timeline  
  **Parameters:** contact_id, event_type, event_data, related_id, user_visible  
**Returns:** {'success': bool, 'event_id': row_id} or error

```python
@anvil.server.callable
def log_contact_event(contact_id, event_type, event_data=None, related_id=None, user_visible=True):
  """Log event to contact timeline"""
  try:
    user = anvil.users.get_user()
    if not user:
      return {'success': False, 'error': 'Not authenticated'}

    contact = app_tables.contacts.get_by_id(contact_id)
    if not contact or contact['instance_id'] != user:
      return {'success': False, 'error': 'Contact not found'}

    event = app_tables.contact_events.add_row(
      contact_id=contact,
      event_type=event_type,
      event_date=datetime.now(),
      event_data=event_data or {},
      related_id=related_id,
      user_visible=user_visible
    )

    # Update last contact date
    contact['last_contact_date'] = datetime.now()

    return {'success': True, 'event_id': event.get_id()}

  except Exception as e:
    print(f"Error logging event: {e}")
    return {'success': False, 'error': str(e)}
```

---

  ## Function: get_recent_activity()

  **Server:** server_customers/timeline_service.py  
  **Purpose:** Get recent activity across all contacts  
  **Parameters:** days (int, default 7)  
**Returns:** List of recent events

```python
@anvil.server.callable
def get_recent_activity(days=7):
  """Get recent activity for all contacts"""
  try:
    user = anvil.users.get_user()
    if not user:
      return {'success': False, 'error': 'Not authenticated'}

    date_threshold = datetime.now() - timedelta(days=days)

    # Get all contacts for this user
    contacts = app_tables.contacts.search(instance_id=user)

    # Get recent events for these contacts
    all_events = []
    for contact in contacts:
      events = app_tables.contact_events.search(
        contact_id=contact,
        event_date=q.greater_than(date_threshold),
        user_visible=True
      )

      for event in events:
        all_events.append({
          'contact_name': f"{contact['first_name']} {contact['last_name']}",
          'contact_email': contact['email'],
          'event_type': event['event_type'],
          'event_date': event['event_date'],
          'event_data': event['event_data']
        })
    
    # Sort by date
    all_events.sort(key=lambda x: x['event_date'], reverse=True)
    
    return {'success': True, 'activity': all_events[:50]}  # Return top 50
    
  except Exception as e:
    print(f"Error getting recent activity: {e}")
    return {'success': False, 'error': str(e)}
```

---

## Function: get_contact_campaigns()

**Server:** server_customers/timeline_service.py  
**Purpose:** Get active campaigns for contact  
**Parameters:** contact_id (row ID)  
**Returns:** List of campaign enrollments

```python
@anvil.server.callable
def get_contact_campaigns(contact_id):
  """Get active campaigns for contact"""
  try:
    user = anvil.users.get_user()
    if not user:
      return {'success': False, 'error': 'Not authenticated'}
    
    contact = app_tables.contacts.get_by_id(contact_id)
    if not contact or contact['instance_id'] != user:
      return {'success': False, 'error': 'Contact not found'}
    
    enrollments = app_tables.contact_campaigns.search(
      contact_id=contact,
      status='Active'
    )
    
    campaign_list = []
    for enrollment in enrollments:
      campaign = enrollment['campaign_id']
      campaign_list.append({
        'campaign_name': campaign['campaign_name'],
        'campaign_type': campaign['campaign_type'],
        'sequence_day': enrollment['sequence_day'],
        'enrolled_date': enrollment['enrolled_date'],
        'last_email_sent': enrollment['last_email_sent_date']
      })
    
    return {'success': True, 'campaigns': campaign_list}
    
  except Exception as e:
    print(f"Error getting contact campaigns: {e}")
    return {'success': False, 'error': str(e)}
```# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#
