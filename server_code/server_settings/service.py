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
from datetime import datetime

@anvil.server.callable
@anvil.users.login_required
def get_business_profile():
  """Get business profile for current client"""
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    config = app_tables.config.get(key='business_profile')

    if config:
      return {'success': True, 'data': config['value']}
    else:
      return {'success': True, 'data': None}

  except Exception as e:
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def save_business_profile(profile_data):
  """Save business profile"""
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    config = app_tables.config.get(key='business_profile')

    if config:
      config['value'] = profile_data
      config['updated_at'] = datetime.now()
      config['updated_by'] = user
      config.update()
    else:
      app_tables.config.add_row(
        key='business_profile',
        value=profile_data,
        category='client',
        updated_at=datetime.now(),
        updated_by=user
      )

    return {'success': True}

  except Exception as e:
    return {'success': False, 'error': str(e)}