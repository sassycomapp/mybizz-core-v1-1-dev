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


## Function: create_campaign()

**Server:** server_marketing/campaign_service.py  
**Purpose:** Create new email campaign  
  **Parameters:** campaign_data (dict)  
**Returns:** {'success': bool, 'campaign_id': row_id} or error

```python
@anvil.server.callable
def create_campaign(campaign_data):
  """Create new email campaign"""
  try:
    user = anvil.users.get_user()
    if not user:
      return {'success': False, 'error': 'Not authenticated'}

    campaign = app_tables.email_campaigns.add_row(
      instance_id=user,
      campaign_name=campaign_data['campaign_name'],
      campaign_type=campaign_data['campaign_type'],
      status='Active',
      emails_sent=0,
      opens=0,
      clicks=0,
      conversions=0,
      revenue_generated=0,
      created_date=datetime.now(),
      last_run_date=None,
      campaign_settings=campaign_data.get('settings', {})
    )

    return {'success': True, 'campaign_id': campaign.get_id()}

  except Exception as e:
    print(f"Error creating campaign: {e}")
    return {'success': False, 'error': str(e)}
```

---

  ## Function: enroll_contact_in_campaign()

  **Server:** server_marketing/campaign_service.py  
  **Purpose:** Enroll contact in campaign  
**Parameters:** contact_id, campaign_id  
**Returns:** {'success': bool, 'enrollment_id': row_id} or error

```python
@anvil.server.callable
def enroll_contact_in_campaign(contact_id, campaign_id):
  """Enroll contact in email campaign"""
  try:
    user = anvil.users.get_user()
    if not user:
      return {'success': False, 'error': 'Not authenticated'}

    contact = app_tables.contacts.get_by_id(contact_id)
    campaign = app_tables.email_campaigns.get_by_id(campaign_id)

    if not contact or contact['instance_id'] != user:
      return {'success': False, 'error': 'Contact not found'}
    if not campaign or campaign['instance_id'] != user:
      return {'success': False, 'error': 'Campaign not found'}

    # Check if already enrolled
    existing = app_tables.contact_campaigns.get(
      contact_id=contact,
      campaign_id=campaign,
      status='Active'
    )
    if existing:
      return {'success': False, 'error': 'Contact already enrolled'}

    # Enroll
    enrollment = app_tables.contact_campaigns.add_row(
      contact_id=contact,
      campaign_id=campaign,
      sequence_day=1,
      status='Active',
      enrolled_date=datetime.now(),
      last_email_sent_date=None,
      completed_date=None
    )

    return {'success': True, 'enrollment_id': enrollment.get_id()}

  except Exception as e:
    print(f"Error enrolling contact: {e}")
    return {'success': False, 'error': str(e)}
```

---

  ## Function: process_campaigns()

  **Server:** server_marketing/campaign_service.py  
  **Purpose:** Background task to process active campaigns (hourly)  
**Returns:** None

```python
@anvil.server.background_task
def process_campaigns():
  """Process all active campaign enrollments (run hourly)"""
  enrollments = app_tables.contact_campaigns.search(status='Active')

  for enrollment in enrollments:
    try:
      campaign = enrollment['campaign_id']

      # Check if next email should be sent
      if should_send_next_email(enrollment):
        send_campaign_email(
          contact=enrollment['contact_id'],
          campaign=campaign,
          sequence_day=enrollment['sequence_day']
        )

        # Update enrollment
        enrollment['sequence_day'] += 1
        enrollment['last_email_sent_date'] = datetime.now()

        # Check if campaign complete
        max_days = campaign['campaign_settings'].get('sequence_length', 7)
        if enrollment['sequence_day'] > max_days:
          enrollment['status'] = 'Completed'
          enrollment['completed_date'] = datetime.now()

    except Exception as e:
      print(f"Error processing campaign enrollment: {e}")
```

---

  ## Function: send_campaign_email()

  **Server:** server_marketing/campaign_service.py  
    **Purpose:** Send individual campaign email  
    **Parameters:** contact, campaign, sequence_day  
    **Returns:** bool

    ```python
    def send_campaign_email(contact, campaign, sequence_day):
    """Send campaign email to contact"""
    try:
    # Get email template for this sequence day
    settings = campaign['campaign_settings']
    email_sequence = settings.get('email_sequence', [])

                   if sequence_day > len(email_sequence):
return False

email_template = email_sequence[sequence_day - 1]

# Send via Brevo
from . import brevo_integration
result = brevo_integration.send_email(
  to_email=contact['email'],
  to_name=f"{contact['first_name']} {contact['last_name']}",
  subject=email_template['subject'],
  html_content=email_template['html_content'],
  campaign_id=campaign.get_id()
)

# Log event
app_tables.contact_events.add_row(
  contact_id=contact,
  event_type='email_sent',
  event_date=datetime.now(),
  event_data={
    'campaign_name': campaign['campaign_name'],
    'sequence_day': sequence_day,
    'subject': email_template['subject']
  },
  related_id=str(campaign.get_id()),
  user_visible=True
)

# Update campaign stats
campaign['emails_sent'] = (campaign['emails_sent'] or 0) + 1
campaign['last_run_date'] = datetime.now()

return True

except Exception as e:
print(f"Error sending campaign email: {e}")
return False
```

---

  ## Function: check_campaign_triggers()

  **Server:** server_marketing/campaign_service.py  
  **Purpose:** Check if contact qualifies for campaign enrollment  
                                          **Parameters:** contact_email, trigger_type  
  **Returns:** None (auto-enrolls if qualified)

  ```python
  @anvil.server.callable
  def check_campaign_triggers(contact_email, trigger_type):
  """Check if contact should be enrolled in campaign based on trigger"""
  try:
  user = anvil.users.get_user()
  if not user:
  return

  contact = app_tables.contacts.get(
    instance_id=user,
    email=contact_email
  )
  if not contact:
  return

  # Find campaigns with this trigger type
  campaigns = app_tables.email_campaigns.search(
    instance_id=user,
    status='Active',
    campaign_type=trigger_type
  )

  for campaign in campaigns:
  # Check if already enrolled
  existing = app_tables.contact_campaigns.get(
    contact_id=contact,
    campaign_id=campaign,
    status='Active'
  )

  if not existing:
  # Auto-enroll
  enroll_contact_in_campaign(contact.get_id(), campaign.get_id())

    except Exception as e:
    print(f"Error checking campaign triggers: {e}")
    ```

    ---

    ## Function: unenroll_contact()

    **Server:** server_marketing/campaign_service.py  
  **Purpose:** Unenroll contact from campaign (unsubscribe)  
                                          **Parameters:** contact_id, campaign_id  
                                          **Returns:** {'success': bool} or error

```python
@anvil.server.callable
def unenroll_contact(contact_id, campaign_id):
  """Unenroll contact from campaign"""
  try:
    enrollment = app_tables.contact_campaigns.get(
      contact_id=app_tables.contacts.get_by_id(contact_id),
      campaign_id=app_tables.email_campaigns.get_by_id(campaign_id),
      status='Active'
    )

    if enrollment:
      enrollment['status'] = 'Unsubscribed'
      enrollment['completed_date'] = datetime.now()

      # Log event
      app_tables.contact_events.add_row(
        contact_id=enrollment['contact_id'],
        event_type='unsubscribed',
        event_date=datetime.now(),
        event_data={'campaign_name': enrollment['campaign_id']['campaign_name']},
        related_id=str(campaign_id),
        user_visible=False
      )

    return {'success': True}

  except Exception as e:
    print(f"Error unenrolling contact: {e}")
    return {'success': False, 'error': str(e)}
```

---

  ## Function: get_campaign_stats()

  **Server:** server_marketing/campaign_service.py  
  **Purpose:** Get statistics for campaign  
  **Parameters:** campaign_id  
**Returns:** dict with campaign metrics

```python
@anvil.server.callable
def get_campaign_stats(campaign_id):
  """Get campaign performance stats"""
  try:
    user = anvil.users.get_user()
    if not user:
      return {'success': False, 'error': 'Not authenticated'}
    
    campaign = app_tables.email_campaigns.get_by_id(campaign_id)
    if not campaign or campaign['instance_id'] != user:
      return {'success': False, 'error': 'Campaign not found'}
    
    # Count enrollments
    total_enrolled = len(list(app_tables.contact_campaigns.search(
      campaign_id=campaign
    )))
    
    active = len(list(app_tables.contact_campaigns.search(
      campaign_id=campaign,
      status='Active'
    )))
    
    completed = len(list(app_tables.contact_campaigns.search(
      campaign_id=campaign,
      status='Completed'
    )))
    
    unsubscribed = len(list(app_tables.contact_campaigns.search(
      campaign_id=campaign,
      status='Unsubscribed'
    )))
    
    stats = {
      'campaign_name': campaign['campaign_name'],
      'campaign_type': campaign['campaign_type'],
      'status': campaign['status'],
      'total_enrolled': total_enrolled,
      'active': active,
      'completed': completed,
      'unsubscribed': unsubscribed,
      'emails_sent': campaign['emails_sent'] or 0,
      'opens': campaign['opens'] or 0,
      'clicks': campaign['clicks'] or 0,
      'conversions': campaign['conversions'] or 0,
      'revenue_generated': campaign['revenue_generated'] or 0,
      'open_rate': (campaign['opens'] / campaign['emails_sent'] * 100) if campaign['emails_sent'] > 0 else 0,
      'click_rate': (campaign['clicks'] / campaign['emails_sent'] * 100) if campaign['emails_sent'] > 0 else 0,
      'created_date': campaign['created_date'],
      'last_run_date': campaign['last_run_date']
    }
    
    return {'success': True, 'stats': stats}
    
  except Exception as e:
    print(f"Error getting campaign stats: {e}")
    return {'success': False, 'error': str(e)}
```

---

## Function: pause_campaign()

**Server:** server_marketing/campaign_service.py  
**Purpose:** Pause active campaign  
**Parameters:** campaign_id  
**Returns:** {'success': bool} or error

```python
@anvil.server.callable
def pause_campaign(campaign_id):
  """Pause active campaign"""
  try:
    user = anvil.users.get_user()
    if not user:
      return {'success': False, 'error': 'Not authenticated'}
    
    campaign = app_tables.email_campaigns.get_by_id(campaign_id)
    if not campaign or campaign['instance_id'] != user:
      return {'success': False, 'error': 'Campaign not found'}
    
    campaign['status'] = 'Paused'
    
    return {'success': True}
    
  except Exception as e:
    print(f"Error pausing campaign: {e}")
    return {'success': False, 'error': str(e)}
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
