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
def get_broadcast_recipient_count(recipient_type, tier_id=None):
  """Get count of recipients for broadcast"""
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    if recipient_type == 'all':
      # All members
      members = list(app_tables.memberships.search())
    elif recipient_type == 'tier':
      # Specific tier
      tier = app_tables.membership_tiers.get_by_id(tier_id)
      members = list(app_tables.memberships.search(tier_id=tier))
    elif recipient_type == 'active':
      # Active only
      members = list(app_tables.memberships.search(status='active'))
    else:
      members = []

    return {'success': True, 'count': len(members)}

  except Exception as e:
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def send_member_broadcast(broadcast_data):
  """Send broadcast email to members"""
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    recipient_type = broadcast_data['recipient_type']
    tier_id = broadcast_data.get('tier_id')

    # Get recipients
    if recipient_type == 'all':
      members = list(app_tables.memberships.search())
    elif recipient_type == 'tier':
      tier = app_tables.membership_tiers.get_by_id(tier_id)
      members = list(app_tables.memberships.search(tier_id=tier))
    elif recipient_type == 'active':
      members = list(app_tables.memberships.search(status='active'))
    else:
      return {'success': False, 'error': 'Invalid recipient type'}

    # Send emails
    sent_count = 0
    for member in members:
      member_user = member['member_id']

      try:
        anvil.email.send(
          to=member_user['email'],
          subject=broadcast_data['subject'],
          text=broadcast_data['message']
        )
        sent_count += 1
      except Exception as e:
        print(f"Failed to send to {member_user['email']}: {e}")

    return {'success': True, 'sent_count': sent_count}

  except Exception as e:
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def get_membership_tiers():
  """Get all membership tiers"""
  try:
    tiers = list(app_tables.membership_tiers.search())
    return {'success': True, 'data': tiers}
  except Exception as e:
    return {'success': False, 'error': str(e)}