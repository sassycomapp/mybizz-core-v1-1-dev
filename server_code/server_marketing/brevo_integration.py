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

# This is a server module. It runs on the Anvil server,
# MODULE 6: server_marketing/brevo_integration.py

**Purpose:** Brevo API wrapper for email sending

  **Module Imports:**
  ```python
    import anvil.server
    import anvil.http
  from anvil.tables import app_tables
                               ```

                               ---

                               ## Function: send_email()

                               **Server:** server_marketing/brevo_integration.py  
                               **Purpose:** Send email via Brevo API  
                               **Parameters:** to_email, to_name, subject, html_content, campaign_id (optional)  
  **Returns:** bool

  ```python
  def send_email(to_email, to_name, subject, html_content, campaign_id=None):
  """Send email via Brevo API"""
  try:
  # Get API key from settings
  settings = app_tables.tbl_system_settings.get(setting_key='brevo_api_key')
  if not settings:
  print("Brevo API key not configured")
  return False

  api_key = settings['setting_value']

          # Prepare request
          url = "https://api.brevo.com/v3/smtp/email"
              headers = {
              'accept': 'application/json',
              'api-key': api_key,
                'content-type': 'application/json'
                }

                payload = {
                'sender': {
                  'name': 'MyBizz',
                  'email': 'noreply@mybizz.com'
                },
                'to': [{
                  'email': to_email,
                  'name': to_name
                }],
                'subject': subject,
                'htmlContent': html_content
                }

                # Add campaign tag if provided
                if campaign_id:
                payload['tags'] = [f'campaign_{campaign_id}']

                # Send request
                response = anvil.http.request(
                  url,
                  method='POST',
                  headers=headers,
                  json=payload
                )

                  return response.status_code == 201

                    except Exception as e:
                    print(f"Error sending email via Brevo: {e}")
                    return False
                    ```

                    ---

                    ## Function: track_email_open()

                    **Server:** server_marketing/brevo_integration.py  
                         **Purpose:** Webhook handler for email opens  
                **Parameters:** webhook_data  
                **Returns:** None

                ```python
                @anvil.server.callable
                def track_email_open(webhook_data):
                """Handle Brevo email open webhook"""
                try:
                email = webhook_data.get('email')
    campaign_tag = webhook_data.get('tag', '')
    
    # Extract campaign_id from tag
    if campaign_tag.startswith('campaign_'):
      campaign_id = campaign_tag.replace('campaign_', '')
      
      # Update campaign stats
      campaign = app_tables.email_campaigns.get_by_id(campaign_id)
      if campaign:
        campaign['opens'] = (campaign['opens'] or 0) + 1
      
      # Log event
      contact = app_tables.contacts.get(email=email)
      if contact:
        app_tables.contact_events.add_row(
          contact_id=contact,
          event_type='email_opened',
          event_date=datetime.now(),
          event_data={'campaign_id': campaign_id},
          related_id=campaign_id,
          user_visible=False
        )
  
  except Exception as e:
    print(f"Error tracking email open: {e}")
```

---

## Function: track_email_click()

**Server:** server_marketing/brevo_integration.py  
**Purpose:** Webhook handler for email clicks  
**Parameters:** webhook_data  
**Returns:** None

```python
@anvil.server.callable
def track_email_click(webhook_data):
  """Handle Brevo email click webhook"""
  try:
    email = webhook_data.get('email')
    campaign_tag = webhook_data.get('tag', '')
    link = webhook_data.get('link', '')
    
    # Extract campaign_id from tag
    if campaign_tag.startswith('campaign_'):
      campaign_id = campaign_tag.replace('campaign_', '')
      
      # Update campaign stats
      campaign = app_tables.email_campaigns.get_by_id(campaign_id)
      if campaign:
        campaign['clicks'] = (campaign['clicks'] or 0) + 1
      
      # Log event
      contact = app_tables.contacts.get(email=email)
      if contact:
        app_tables.contact_events.add_row(
          contact_id=contact,
          event_type='email_clicked',
          event_date=datetime.now(),
          event_data={'campaign_id': campaign_id, 'link': link},
          related_id=campaign_id,
          user_visible=False
        )
  
  except Exception as e:
    print(f"Error tracking email click: {e}")
```
          ## Function: should_send_next_email()

          **Server:** server_marketing/campaign_service.py  
              **Purpose:** Check if next email in sequence should be sent  
        **Parameters:** enrollment (Row object)  
         **Returns:** bool

                 ```python
                 def should_send_next_email(enrollment):
                 """Check if next email should be sent based on timing rules"""
                   try:
                   # If no email sent yet, send first
                   if not enrollment['last_email_sent_date']:
                   return True

                   # Get campaign settings
                   campaign = enrollment['campaign_id']
                   settings = campaign['campaign_settings']

                            # Check delay between emails (default 1 day)
                            delay_days = settings.get('email_delay_days', 1)
                                       next_send_date = enrollment['last_email_sent_date'] + timedelta(days=delay_days)

                                         return datetime.now() >= next_send_date

                                         except Exception as e:
                                         print(f"Error checking email timing: {e}")
                                         return False
                                         ```
---
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
