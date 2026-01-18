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


# MODULE 5: server_marketing/task_service.py

**Purpose:** Task management for follow-ups

                             **Module Imports:**
                             ```python
                               import anvil.server
                               import anvil.users
                               import anvil.tables as tables
from anvil.tables import app_tables
from datetime import datetime, timedelta
```

---

  ## Function: create_task()

  **Server:** server_marketing/task_service.py  
  **Purpose:** Create new task  
  **Parameters:** task_data (dict)  
  **Returns:** {'success': bool, 'task_id': row_id} or error

```python
@anvil.server.callable
def create_task(task_data):
  """Create new task"""
  try:
    user = anvil.users.get_user()
    if not user:
      return {'success': False, 'error': 'Not authenticated'}

    # Get contact if provided
    contact = None
    if task_data.get('contact_id'):
      contact = app_tables.contacts.get_by_id(task_data['contact_id'])

    task = app_tables.tasks.add_row(
      instance_id=user,
      contact_id=contact,  # Can be None
      task_title=task_data['task_title'],
      task_type=task_data.get('task_type', 'custom'),
      due_date=task_data['due_date'],
      completed=False,
      completed_date=None,
      notes=task_data.get('notes', ''),
      auto_generated=task_data.get('auto_generated', False),
      created_at=datetime.now()
    )

    return {'success': True, 'task_id': task.get_id()}

  except Exception as e:
    print(f"Error creating task: {e}")
    return {'success': False, 'error': str(e)}
```

---

  ## Function: get_all_tasks()

  **Server:** server_marketing/task_service.py  
  **Purpose:** Get all tasks with filters  
  **Parameters:** filters (dict)  
  **Returns:** List of tasks

  ```python
  @anvil.server.callable
  def get_all_tasks(filters=None):
    """Get all tasks"""
    try:
      user = anvil.users.get_user()
      if not user:
        return {'success': False, 'error': 'Not authenticated'}

      query = {'instance_id': user}

      # Apply filters
      if filters:
        if filters.get('completed') is not None:
          query['completed'] = filters['completed']
        if filters.get('overdue'):
          query['due_date'] = q.less_than(datetime.now().date())
          query['completed'] = False

      tasks = app_tables.tasks.search(
        tables.order_by('due_date'),
        **query
      )

      task_list = []
      for task in tasks:
        task_data = {
          'task_id': task.get_id(),
          'task_title': task['task_title'],
          'task_type': task['task_type'],
          'due_date': task['due_date'],
          'completed': task['completed'],
          'completed_date': task['completed_date'],
          'notes': task['notes'],
          'auto_generated': task['auto_generated']
        }

        # Add contact info if linked
        if task['contact_id']:
          contact = task['contact_id']
          task_data['contact_name'] = f"{contact['first_name']} {contact['last_name']}"
          task_data['contact_email'] = contact['email']

        task_list.append(task_data)

      return {'success': True, 'tasks': task_list}

    except Exception as e:
      print(f"Error getting tasks: {e}")
      return {'success': False, 'error': str(e)}
```

---

  ## Function: complete_task()

  **Server:** server_marketing/task_service.py  
  **Purpose:** Mark task as completed  
  **Parameters:** task_id  
  **Returns:** {'success': bool} or error

```python
@anvil.server.callable
def complete_task(task_id):
  """Mark task as completed"""
  try:
    user = anvil.users.get_user()
    if not user:
      return {'success': False, 'error': 'Not authenticated'}

    task = app_tables.tasks.get_by_id(task_id)
    if not task or task['instance_id'] != user:
      return {'success': False, 'error': 'Task not found'}

    task['completed'] = True
    task['completed_date'] = datetime.now()

    # Log event if task is linked to contact
    if task['contact_id']:
      app_tables.contact_events.add_row(
        contact_id=task['contact_id'],
        event_type='task_completed',
        event_date=datetime.now(),
        event_data={'task_title': task['task_title'], 'task_type': task['task_type']},
        related_id=str(task_id),
        user_visible=True
      )

    return {'success': True}

  except Exception as e:
    print(f"Error completing task: {e}")
    return {'success': False, 'error': str(e)}
```

---

  ## Function: delete_task()

  **Server:** server_marketing/task_service.py  
  **Purpose:** Delete task  
  **Parameters:** task_id  
  **Returns:** {'success': bool} or error

```python
@anvil.server.callable
def delete_task(task_id):
  """Delete task"""
  try:
    user = anvil.users.get_user()
    if not user:
      return {'success': False, 'error': 'Not authenticated'}

    task = app_tables.tasks.get_by_id(task_id)
    if not task or task['instance_id'] != user:
      return {'success': False, 'error': 'Task not found'}

    task.delete()

    return {'success': True}

  except Exception as e:
    print(f"Error deleting task: {e}")
    return {'success': False, 'error': str(e)}
```

---

  ## Function: create_automated_tasks()

  **Server:** server_marketing/task_service.py  
  **Purpose:** Background task to create auto-tasks (daily)  
**Returns:** None

```python
@anvil.server.background_task
def create_automated_tasks():
  """Create automated tasks based on triggers (run daily 3am)"""

  # Example: Create arrival instruction tasks 7 days before booking
  from_date = datetime.now()
  to_date = datetime.now() + timedelta(days=8)

  # This would need to access bookings table
  # Implementation depends on vertical-specific logic
  pass
```

# This is a server module. It runs on the Anvil server,
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
