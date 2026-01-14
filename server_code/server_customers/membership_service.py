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
import qrcode
import io

@anvil.server.callable
@anvil.users.login_required
def get_active_membership():
  """
  Get user's active membership with QR code.
  
  Returns:
    dict: {'success': bool, 'data': membership}
  """
  try:
    user = anvil.users.get_user()

    # Get active membership
    membership = app_tables.memberships.get(
      member_id=user,
      status='active'
    )

    if not membership:
      return {'success': False, 'error': 'No active membership'}

    # Get tier details
    tier = membership['tier_id']

    # Generate QR code if not exists
    if not membership.get('qr_code'):
      qr_code_data = f"MEMBER:{membership['member_number']}"
      membership['qr_code'] = generate_qr_code(qr_code_data)
      membership.update()

    # Prepare response
    membership_data = {
      'member_number': membership['member_number'],
      'tier': tier['name'],
      'start_date': membership['start_date'],
      'end_date': membership.get('end_date'),
      'qr_code_url': membership.get('qr_code'),
      'benefits': get_tier_benefits(tier.get_id())
    }

    return {'success': True, 'data': membership_data}

  except Exception as e:
    print(f"Error getting membership: {e}")
    return {'success': False, 'error': str(e)}

def generate_qr_code(data):
  """Generate QR code image"""
  try:
    # Create QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)

    # Generate image
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to Anvil Media
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return anvil.BlobMedia('image/png', buffer.read(), name='qr_code.png')

  except Exception as e:
    print(f"Error generating QR code: {e}")
    return None

def get_tier_benefits(tier_id):
  """Get benefits for tier"""
  try:
    benefits = list(
      app_tables.membership_benefits.search(
        tier_id=app_tables.membership_tiers.get_by_id(tier_id),
        is_active=True
      )
    )

    return [b['benefit_value'] for b in benefits]

  except Exception as e:
    print(f"Error getting benefits: {e}")
    return []