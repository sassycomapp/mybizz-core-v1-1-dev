from ._anvil_designer import BookingRowTemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class BookingRowTemplate(BookingRowTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    # Display data
    self.lbl_booking_number.text = self.item['booking_number']
    self.lbl_customer.text = self.item['customer_name']
    self.lbl_resource.text = self.item['resource_name']
    self.lbl_datetime.text = self.item['datetime_display']

    # Status with emoji
    status_text = self.item['status'].capitalize()
    status_emoji = {
      'pending': '🟧',
      'confirmed': '✅',
      'completed': '✔️',
      'cancelled': '❌',
      'no_show': '⚠️'
    }
    self.lbl_status.text = f"{status_emoji.get(self.item['status'], '⚪')} {status_text}"

    # Actions button
    self.btn_actions.text = "⋮"
    self.btn_actions.role = "secondary-color"

  def button_actions_click(self, **event_args):
    """Show action menu"""
    status = self.item['status']

    # Build action menu based on status
    actions = []

    if status == 'pending':
      actions.append(('✅ Confirm Booking', 'confirm'))
      actions.append(('❌ Cancel', 'cancel'))
    elif status == 'confirmed':
      actions.append(('✔️ Mark Completed', 'complete'))
      actions.append(('⚠️ Mark No-Show', 'no_show'))
      actions.append(('❌ Cancel', 'cancel'))

    actions.append(('✏️ Edit', 'edit'))
    actions.append(('👁️ View Details', 'view'))

    # Show menu
    choice = alert(
      content=ColumnPanel(),
      title=f"Actions for {self.item['booking_number']}",
      buttons=actions + [("Close", None)]
    )

    if choice:
      self.handle_action(choice)

  def handle_action(self, action):
    """Handle selected action"""
    try:
      if action == 'edit':
        open_form('bookings.BookingCreateForm', booking_id=self.item.get_id())

      elif action == 'view':
        alert(f"Booking Details:\n\n{self.item['booking_number']}\nCustomer: {self.item['customer_name']}\nResource: {self.item['resource_name']}")
        # TODO: Open BookingDetailForm

      elif action == 'confirm':
        if confirm(f"Confirm booking {self.item['booking_number']}?"):
          anvil.server.call('update_booking_status', self.item.get_id(), 'confirmed')
          Notification("Booking confirmed!", style="success").show()
          self.parent.raise_event('x-refresh-bookings')

      elif action == 'complete':
        if confirm(f"Mark {self.item['booking_number']} as completed?"):
          anvil.server.call('update_booking_status', self.item.get_id(), 'completed')
          Notification("Booking completed!", style="success").show()
          self.parent.raise_event('x-refresh-bookings')

      elif action == 'no_show':
        if confirm(f"Mark {self.item['booking_number']} as no-show?"):
          anvil.server.call('update_booking_status', self.item.get_id(), 'no_show')
          Notification("Marked as no-show", style="warning").show()
          self.parent.raise_event('x-refresh-bookings')

      elif action == 'cancel':
        reason = alert(
          content=TextArea(placeholder="Reason for cancellation (optional)"),
          title="Cancel Booking",
          buttons=[("Cancel Action", False), ("Confirm Cancel", True)]
        )
        if reason:
          anvil.server.call('cancel_booking', self.item.get_id(), reason.text if hasattr(reason, 'text') else '')
          Notification("Booking cancelled", style="info").show()
          self.parent.raise_event('x-refresh-bookings')

    except Exception as e:
      alert(f"Error: {str(e)}")