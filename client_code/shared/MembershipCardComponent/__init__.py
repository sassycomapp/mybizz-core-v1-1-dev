from ._anvil_designer import MembershipCardComponentTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class MembershipCardComponent(MembershipCardComponentTemplate):
  """Digital membership card display"""

  def __init__(self, **properties):
    self.init_components(**properties)

    # Check authentication
    user = anvil.users.get_user()
    if not user:
      alert("Please login to view your membership card")
      return

    # Card styling
    self.col_card.background = "#F5F5F5"
    self.col_card.border = "2px solid #FFD700"  # Gold border
    self.col_card.spacing = "medium"
    self.col_card.role = "card"

    # Load membership
    self.load_membership()

  def load_membership(self):
    """Load member's active membership"""
    try:
      result = anvil.server.call('get_active_membership')

      if result['success']:
        membership = result['data']

        # Tier header
        tier = membership.get('tier', 'Basic').upper()
        self.lbl_tier.text = f"{tier} MEMBER"
        self.lbl_tier.font_size = 24
        self.lbl_tier.bold = True
        self.lbl_tier.align = "center"

        # Set tier color
        tier_colors = {
          'BASIC': '#999999',
          'SILVER': '#C0C0C0',
          'GOLD': '#FFD700',
          'PLATINUM': '#E5E4E2'
        }
        self.lbl_tier.foreground = tier_colors.get(tier, '#999999')

        # Member info
        user = anvil.users.get_user()
        member_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or user.get('email')

        self.lbl_member_name.text = member_name
        self.lbl_member_name.font_size = 20
        self.lbl_member_name.bold = True

        self.lbl_member_number.text = f"Member #: {membership['member_number']}"
        self.lbl_member_number.font_size = 14
        self.lbl_member_number.foreground = "#666666"

        # QR code
        qr_code_url = membership.get('qr_code_url')
        if qr_code_url:
          self.img_qr_code.source = qr_code_url
          self.img_qr_code.height = 120
          self.img_qr_code.width = 120

        # Tier and dates
        self.lbl_tier_name.text = f"Tier: {membership.get('tier', 'Basic').title()}"
        self.lbl_tier_name.font_size = 14

        joined_date = membership['start_date'].strftime('%b %d, %Y')
        self.lbl_joined_date.text = f"Joined: {joined_date}"
        self.lbl_joined_date.font_size = 14

        if membership.get('end_date'):
          expiry_date = membership['end_date'].strftime('%b %d, %Y')
          self.lbl_expiry_date.text = f"Expires: {expiry_date}"
          self.lbl_expiry_date.font_size = 14
        else:
          self.lbl_expiry_date.text = "Expires: Never"
          self.lbl_expiry_date.font_size = 14

        # Benefits
        benefits = membership.get('benefits', [])
        if benefits:
          benefits_text = "Benefits:\n" + "\n".join([f"• {b}" for b in benefits])
          self.lbl_benefits.text = benefits_text
          self.lbl_benefits.font_size = 14
        else:
          self.lbl_benefits.visible = False

      else:
        # No active membership
        alert("You don't have an active membership")

    except Exception as e:
      print(f"Error loading membership: {e}")
      alert(f"Failed to load membership: {str(e)}")