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
from datetime import datetime, timedelta


## Function: create_segment()

**Server:** server_customers/segment_service.py  
**Purpose:** Create custom contact segment  
  **Parameters:** segment_data (dict with segment_name, filter_criteria)  
**Returns:** {'success': bool, 'segment_id': row_id} or error

```python
@anvil.server.callable
def create_segment(segment_data):
  """Create custom segment"""
  try:
    user = anvil.users.get_user()
    if not user:
      return {'success': False, 'error': 'Not authenticated'}

    segment = app_tables.segments.add_row(
      instance_id=user,
      segment_name=segment_data['segment_name'],
      segment_type='Custom',
      filter_criteria=segment_data['filter_criteria'],
      contact_count=0,
      is_active=True,
      created_date=datetime.now()
    )

    # Calculate initial count
    count = get_segment_count(segment.get_id())
    segment['contact_count'] = count

    return {'success': True, 'segment_id': segment.get_id()}

  except Exception as e:
    print(f"Error creating segment: {e}")
    return {'success': False, 'error': str(e)}
```

---

  ## Function: get_segment_contacts()

  **Server:** server_customers/segment_service.py  
  **Purpose:** Get all contacts matching segment criteria  
  **Parameters:** segment_id (row ID)  
**Returns:** List of contacts or error

```python
@anvil.server.callable
def get_segment_contacts(segment_id):
  """Get all contacts in segment"""
  try:
    user = anvil.users.get_user()
    if not user:
      return {'success': False, 'error': 'Not authenticated'}

    segment = app_tables.segments.get_by_id(segment_id)
    if not segment or segment['instance_id'] != user:
      return {'success': False, 'error': 'Segment not found'}

    # Build query from filter criteria
    query = {'instance_id': user}
    criteria = segment['filter_criteria']

    if criteria.get('status'):
      query['status'] = q.any_of(*criteria['status'])

    if criteria.get('lifecycle_stage'):
      query['lifecycle_stage'] = q.any_of(*criteria['lifecycle_stage'])

    if criteria.get('total_spent_min'):
      query['total_spent'] = q.greater_than(criteria['total_spent_min'])

    if criteria.get('days_since_contact'):
      date_threshold = datetime.now() - timedelta(days=criteria['days_since_contact'])
      query['last_contact_date'] = q.less_than(date_threshold)

    contacts = app_tables.contacts.search(**query)

    return {'success': True, 'contacts': list(contacts)}

  except Exception as e:
    print(f"Error getting segment contacts: {e}")
    return {'success': False, 'error': str(e)}
```

---

  ## Function: get_segment_count()

  **Server:** server_customers/segment_service.py  
  **Purpose:** Count contacts in segment  
**Parameters:** segment_id (row ID)  
**Returns:** Integer count

```python
@anvil.server.callable
def get_segment_count(segment_id):
  """Get count of contacts in segment"""
  try:
    result = get_segment_contacts(segment_id)
    if result['success']:
      return len(result['contacts'])
    return 0
  except:
    return 0
```

---

  ## Function: update_segment_counts()

  **Server:** server_customers/segment_service.py  
  **Purpose:** Update cached contact counts for all segments (background task)  
  **Returns:** None

  ```python
  @anvil.server.background_task
    def update_segment_counts():
    """Background task to update segment counts (run nightly)"""
    for segment in app_tables.segments.search(is_active=True):
    try:
    count = get_segment_count(segment.get_id())
    segment['contact_count'] = count
except Exception as e:
print(f"Error updating segment count: {e}")
```

---

  ## Pre-Built Segment Queries

  **Server:** server_customers/segment_service.py  
  **Purpose:** Pre-defined segments for each vertical

    ```python
    # Hospitality Segments
    def get_vip_guests(user):
    """Guests with 3+ bookings"""
    return len(list(app_tables.contacts.search(
    instance_id=user,
    total_transactions=q.greater_than_or_equal_to(3)
)))

def get_repeat_guests(user):
  """Guests with 2+ bookings"""
  return len(list(app_tables.contacts.search(
    instance_id=user,
    total_transactions=q.greater_than_or_equal_to(2)
  )))

def get_lost_guests(user):
  """No contact in 180+ days"""
  date_threshold = datetime.now() - timedelta(days=180)
  return len(list(app_tables.contacts.search(
    instance_id=user,
    last_contact_date=q.less_than(date_threshold)
  )))

# E-commerce Segments
def get_high_value_customers(user):
  """Customers with 5000+ total spent"""
  return len(list(app_tables.contacts.search(
    instance_id=user,
    total_spent=q.greater_than_or_equal_to(5000)
  )))

def get_repeat_buyers(user):
  """Customers with 2+ orders"""
  return len(list(app_tables.contacts.search(
    instance_id=user,
    total_transactions=q.greater_than_or_equal_to(2)
  )))
```
