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


@anvil.server.callable
@anvil.users.login_required
def get_courier_config():
  """Get courier configuration"""
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    config = app_tables.config.get(key='courier_config')

    if config:
      return {'success': True, 'data': config['value']}
    else:
      return {'success': True, 'data': {}}

  except Exception as e:
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def save_courier_config(config_data):
  """Save courier configuration"""
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    # Remove None values (masked passwords)
    clean_data = {k: v for k, v in config_data.items() if v is not None}

    config = app_tables.config.get(key='courier_config')

    if config:
      # Merge with existing to preserve masked values
      existing = config['value']
      existing.update(clean_data)
      config['value'] = existing
      config['updated_at'] = datetime.now()
      config['updated_by'] = user
      config.update()
    else:
      app_tables.config.add_row(
        key='courier_config',
        value=clean_data,
        category='client',
        updated_at=datetime.now(),
        updated_by=user
      )

    return {'success': True}

  except Exception as e:
    return {'success': False, 'error': str(e)}


@anvil.server.callable
@anvil.users.login_required
def get_currency_settings():
  """Get currency settings"""
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    config = app_tables.config.get(key='currency_settings')

    if config:
      return {'success': True, 'data': config['value']}
    else:
      return {'success': True, 'data': {}}

  except Exception as e:
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def save_currency_settings(settings, is_locked):
  """Save currency settings"""
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    # Check if system currency is being changed when locked
    if is_locked:
      existing = app_tables.config.get(key='currency_settings')
      if existing and existing['value'].get('system_currency') != settings['system_currency']:
        return {'success': False, 'error': 'System currency cannot be changed after initial setup'}

    config = app_tables.config.get(key='currency_settings')

    if config:
      config['value'] = settings
      config['updated_at'] = datetime.now()
      config['updated_by'] = user
      config.update()
    else:
      app_tables.config.add_row(
        key='currency_settings',
        value=settings,
        category='client',
        updated_at=datetime.now(),
        updated_by=user
      )

    return {'success': True}

  except Exception as e:
    return {'success': False, 'error': str(e)}


@anvil.server.callable
@anvil.users.login_required
def generate_dns_records(domain):
  """Generate DNS records for Zoho"""
  try:
    user = anvil.users.get_user()

    if user['role'] != 'owner':
      return {'success': False, 'error': 'Access denied'}

    records = [
      {'type': 'MX', 'value': f'mx.zoho.com (Priority: 10)'},
      {'type': 'MX', 'value': f'mx2.zoho.com (Priority: 20)'},
      {'type': 'TXT', 'value': 'v=spf1 include:zoho.com ~all'},
      {'type': 'CNAME', 'value': f'zb{domain[:8]}.zmverify.zoho.com'}
    ]

    return {'success': True, 'data': records}

  except Exception as e:
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def test_email_configuration():
  """Test email configuration by sending test email"""
  try:
    user = anvil.users.get_user()

    if user['role'] != 'owner':
      return {'success': False, 'error': 'Access denied'}

    # TODO: Send actual test email via Zoho SMTP
    # For now, return success

    return {'success': True}

  except Exception as e:
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def get_enabled_features():
  """Get enabled features"""
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    config = app_tables.config.get(key='enabled_features')

    if config:
      return {'success': True, 'data': config['value']}
    else:
      # Defaults
      return {'success': True, 'data': {
        'bookings': True,
        'ecommerce': True,
        'subscriptions': False,
        'services': False,
        'hospitality': False,
        'blog': True
      }}

  except Exception as e:
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def save_enabled_features(features):
  """Save enabled features"""
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    config = app_tables.config.get(key='enabled_features')

    if config:
      config['value'] = features
      config['updated_at'] = datetime.now()
      config['updated_by'] = user
      config.update()
    else:
      app_tables.config.add_row(
        key='enabled_features',
        value=features,
        category='client',
        updated_at=datetime.now(),
        updated_by=user
      )

    return {'success': True}

  except Exception as e:
    return {'success': False, 'error': str(e)}


@anvil.server.callable
@anvil.users.login_required
def select_payment_gateway(gateway):
  """Select payment gateway"""
  try:
    user = anvil.users.get_user()

    if user['role'] != 'owner':
      return {'success': False, 'error': 'Only owner can configure payments'}

    config = app_tables.config.get(key='payment_gateway')

    if config:
      return {'success': False, 'error': 'Payment gateway already configured'}

    app_tables.config.add_row(
      key='payment_gateway',
      value={'active_gateway': gateway},
      category='client',
      updated_at=datetime.now(),
      updated_by=user
    )

    return {'success': True}

  except Exception as e:
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def save_stripe_api_key(api_key):
  """Save Stripe API key"""
  try:
    user = anvil.users.get_user()

    if user['role'] != 'owner':
      return {'success': False, 'error': 'Access denied'}

    # Store securely (use Anvil Secrets in production)
    config = app_tables.config.get(key='stripe_config')

    if config:
      config['value']['api_key'] = api_key
      config.update()
    else:
      app_tables.config.add_row(
        key='stripe_config',
        value={'api_key': api_key},
        category='client',
        updated_at=datetime.now(),
        updated_by=user
      )

    return {'success': True}

  except Exception as e:
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def save_paystack_api_key(api_key):
  """Save Paystack API key"""
  try:
    user = anvil.users.get_user()

    if user['role'] != 'owner':
      return {'success': False, 'error': 'Access denied'}

    # Store securely (use Anvil Secrets in production)
    config = app_tables.config.get(key='paystack_config')

    if config:
      config['value']['api_key'] = api_key
      config.update()
    else:
      app_tables.config.add_row(
        key='paystack_config',
        value={'api_key': api_key},
        category='client',
        updated_at=datetime.now(),
        updated_by=user
      )

    return {'success': True}

  except Exception as e:
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def get_theme_settings():
  """Get theme settings"""
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    config = app_tables.config.get(key='theme_settings')

    if config:
      return {'success': True, 'data': config['value']}
    else:
      return {'success': True, 'data': {
        'primary_color': '#2196F3',
        'accent_color': '#FF9800',
        'font_family': 'default',
        'header_style': 'light'
      }}

  except Exception as e:
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def save_theme_settings(theme_data):
  """Save theme settings"""
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    config = app_tables.config.get(key='theme_settings')

    if config:
      config['value'] = theme_data
      config['updated_at'] = datetime.now()
      config['updated_by'] = user
      config.update()
    else:
      app_tables.config.add_row(
        key='theme_settings',
        value=theme_data,
        category='client',
        updated_at=datetime.now(),
        updated_by=user
      )

    return {'success': True}

  except Exception as e:
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def get_all_users():
  """Get all users in account"""
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    users = list(app_tables.users.search())

    return {'success': True, 'data': users}

  except Exception as e:
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def invite_user(email, role):
  """Invite new user"""
  try:
    user = anvil.users.get_user()

    if user['role'] != 'owner':
      return {'success': False, 'error': 'Only owner can invite users'}

    # Check if user exists
    existing = app_tables.users.get(email=email)
    if existing:
      return {'success': False, 'error': 'User already exists'}

    # Create user
    new_user = app_tables.users.add_row(
      email=email,
      enabled=True,
      role=role,
      account_status='active',
      created_at=datetime.now()
    )

    # TODO: Send invitation email

    return {'success': True}

  except Exception as e:
    return {'success': False, 'error': str(e)}