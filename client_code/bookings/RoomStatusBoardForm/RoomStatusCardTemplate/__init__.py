from ._anvil_designer import RoomStatusCardTemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class RoomStatusCardTemplate(RoomStatusCardTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    # Style card based on status
    status = self.item['display_status']
    colors = {
      'vacant': '#E8F5E9',      # Light green
      'occupied': '#E3F2FD',    # Light blue
      'dirty': '#FFF9C4',       # Light yellow
      'maintenance': '#FFEBEE'  # Light red
    }

    self.col_card.background = colors.get(status, '#FFFFFF')
    self.col_card.border = f"2px solid {self.get_border_color(status)}"

    # Build card content
    self.build_card()

  def get_border_color(self, status):
    """Get border color for status"""
    colors = {
      'vacant': '#4CAF50',
      'occupied': '#2196F3',
      'dirty': '#FFC107',
      'maintenance': '#F44336'
    }
    return colors.get(status, '#CCCCCC')

  def build_card(self):
    """Build card content"""
    self.col_card.clear()

    # Room number
    room_num = Label(
      text=f"Room {self.item['room_number']}",
      bold=True,
      font_size=18
    )
    self.col_card.add_component(room_num)

    # Status with emoji
    status_text = self.item['display_status'].capitalize()
    status_emoji = {
      'vacant': '🟢',
      'occupied': '🔵',
      'dirty': '🟡',
      'maintenance': '🔴'
    }

    status = Label(
      text=f"{status_emoji.get(self.item['display_status'], '⚪')} {status_text}",
      font_size=16,
      bold=True
    )
    self.col_card.add_component(status)

    # Room type
    room_type = Label(
      text=self.item['room_type'],
      foreground="#666666"
    )
    self.col_card.add_component(room_type)

    # Capacity
    capacity = Label(
      text=f"{self.item['capacity']} guests",
      font_size=12,
      foreground="#666666"
    )
    self.col_card.add_component(capacity)

    # Guest info if occupied
    if self.item['display_status'] == 'occupied' and self.item.get('current_guest'):
      guest_label = Label(
        text=self.item['current_guest'],
        spacing_above='small',
        italic=True
      )
      self.col_card.add_component(guest_label)

      if self.item.get('checkout_date'):
        checkout = Label(
          text=f"Out: {self.item['checkout_date']}",
          font_size=12,
          foreground="#666666"
        )
        self.col_card.add_component(checkout)

    # Actions button
    btn_actions = Button(
      text="Actions",
      spacing_above='medium',
      role="outlined-button"
    )
    btn_actions.set_event_handler('click', self.show_actions)
    self.col_card.add_component(btn_actions)

  def show_actions(self, **event_args):
    """Show action menu"""
    status = self.item['display_status']

    # Build action menu based on status
    actions = []

    if status == 'vacant':
      actions.append(('🧹 Mark as Dirty', 'dirty'))
      actions.append(('🔧 Mark Maintenance', 'maintenance'))
    elif status == 'occupied':
      actions.append(('📤 Check Out', 'checkout'))
    elif status == 'dirty':
      actions.append(('✅ Mark Clean (Vacant)', 'vacant'))
    elif status == 'maintenance':
      actions.append(('✅ Mark Ready (Vacant)', 'vacant'))

    actions.append(('👁️ View Details', 'view'))

    # Show menu
    choice = alert(
      content=ColumnPanel(),
      title=f"Room {self.item['room_number']} Actions",
      buttons=actions + [("Close", None)]
    )

    if choice:
      self.handle_action(choice)

  def handle_action(self, action):
    """Handle selected action"""
    try:
      if action == 'view':
        # Show room details
        alert(f"Room {self.item['room_number']}\nType: {self.item['room_type']}\nCapacity: {self.item['capacity']}\nStatus: {self.item['display_status']}")

      elif action == 'checkout':
        # Open checkout form
        if self.item.get('current_booking_id'):
          open_form('bookings.CheckInOutForm', booking_id=self.item['current_booking_id'])

      elif action in ['vacant', 'dirty', 'maintenance']:
        # Update room status
        if confirm(f"Mark room {self.item['room_number']} as {action}?"):
          anvil.server.call('update_room_status', self.item.get_id(), action)
          Notification(f"Room status updated to {action}", style="success").show()
          self.parent.parent.load_rooms()

    except Exception as e:
      alert(f"Error: {str(e)}")