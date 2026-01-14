from ._anvil_designer import MemberBroadcastFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class MemberBroadcastForm(MemberBroadcastFormTemplate):
  """Send broadcast emails to members"""

  def __init__(self, **properties):
    self.init_components(**properties)

    # Check permissions
    user = anvil.users.get_user()
    if not user or user['role'] not in ['owner', 'manager']:
      alert("Access denied")
      return

    self.lbl_title.text = "Member Broadcast"
    self.lbl_title.font_size = 24
    self.lbl_title.bold = True

    # Recipient options
    self.rb_all_members.text = "All Members"
    self.rb_all_members.group_name = "recipients"
    self.rb_all_members.selected = True

    self.rb_specific_tier.text = "Specific Tier:"
    self.rb_specific_tier.group_name = "recipients"

    self.rb_active_only.text = "Active Members Only"
    self.rb_active_only.group_name = "recipients"

    # Load tiers
    self.load_tiers()

    # Subject
    self.txt_subject.placeholder = "Email subject"

    # Message
    self.txt_message.placeholder = "Write your message to members..."
    self.txt_message.rows = 8

    # Preview
    self.lbl_preview.text = "Preview: Calculating..."
    self.lbl_preview.foreground = "#666666"
    self.update_preview()

    # Buttons
    self.btn_send.text = "Send Broadcast"
    self.btn_send.icon = "fa:paper-plane"
    self.btn_send.role = "primary-color"

    self.btn_draft.text = "Save as Draft"
    self.btn_draft.icon = "fa:save"
    self.btn_draft.role = "outlined-button"

  def load_tiers(self):
    """Load membership tiers"""
    try:
      result = anvil.server.call('get_membership_tiers')

      if result['success']:
        tiers = result['data']
        self.dd_tier.items = [(t['name'], t.get_id()) for t in tiers]

    except Exception as e:
      print(f"Error loading tiers: {e}")

  def update_preview(self):
    """Update recipient count preview"""
    try:
      recipient_type = self.get_recipient_type()
      tier_id = self.dd_tier.selected_value if recipient_type == 'tier' else None

      result = anvil.server.call('get_broadcast_recipient_count', recipient_type, tier_id)

      if result['success']:
        count = result['count']
        self.lbl_preview.text = f"Preview: {count} member{'s' if count != 1 else ''} will receive this email"

    except Exception as e:
      print(f"Error updating preview: {e}")

  def get_recipient_type(self):
    """Get selected recipient type"""
    if self.rb_all_members.selected:
      return 'all'
    elif self.rb_specific_tier.selected:
      return 'tier'
    elif self.rb_active_only.selected:
      return 'active'
    return 'all'

  @handle("rb_all_members", "clicked")
  def rb_all_members_clicked(self, **event_args):
    """Update preview when selection changes"""
    self.dd_tier.enabled = False
    self.update_preview()

  @handle("rb_specific_tier", "clicked")
  def rb_specific_tier_clicked(self, **event_args):
    """Enable tier dropdown"""
    self.dd_tier.enabled = True
    self.update_preview()

  @handle("rb_active_only", "clicked")
  def rb_active_only_clicked(self, **event_args):
    """Update preview"""
    self.dd_tier.enabled = False
    self.update_preview()

  @handle("dd_tier", "change")
  def dd_tier_change(self, **event_args):
    """Update preview when tier changes"""
    self.update_preview()

  def validate_broadcast(self):
    """Validate broadcast data"""
    if not self.txt_subject.text:
      alert("Please enter a subject")
      return False

    if not self.txt_message.text:
      alert("Please write a message")
      return False

    return True

  def button_send_click(self, **event_args):
    """Send broadcast"""
    if not self.validate_broadcast():
      return

    # Confirm send
    confirm = alert(
      f"Send this email to members?\n\n{self.lbl_preview.text}",
      title="Confirm Broadcast",
      buttons=[("Send", True), ("Cancel", False)]
    )

    if not confirm:
      return

    try:
      recipient_type = self.get_recipient_type()
      tier_id = self.dd_tier.selected_value if recipient_type == 'tier' else None

      broadcast_data = {
        'subject': self.txt_subject.text,
        'message': self.txt_message.text,
        'recipient_type': recipient_type,
        'tier_id': tier_id
      }

      result = anvil.server.call('send_member_broadcast', broadcast_data)

      if result['success']:
        Notification(f"Broadcast sent to {result['sent_count']} members!", style="success").show()

        # Clear form
        self.txt_subject.text = ''
        self.txt_message.text = ''
      else:
        alert(f"Error: {result.get('error')}")

    except Exception as e:
      alert(f"Failed to send: {str(e)}")

  def button_draft_click(self, **event_args):
    """Save as draft"""
    if not self.txt_subject.text and not self.txt_message.text:
      alert("Nothing to save")
      return

    # TODO: Implement draft saving
    Notification("Draft saved", style="info").show()

  @handle("btn_draft", "click")
  def btn_draft_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_send", "click")
  def btn_send_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
