from ._anvil_designer import RoomRowTemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class RoomRowTemplate(RoomRowTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    # Display room data
    self.lbl_room_number.text = self.item['room_number']
    self.lbl_room_number.bold = True

    self.lbl_type.text = self.item['room_type']

    self.lbl_capacity.text = f"{self.item['capacity']} guests"

    self.lbl_price.text = f"${self.item['price_per_night']:.2f}"

    # Status with color
    status_text = self.item['status'].capitalize()
    self.lbl_status.text = status_text

    if self.item['status'] == 'active':
      self.lbl_status.foreground = "green"
    elif self.item['status'] == 'maintenance':
      self.lbl_status.foreground = "red"
    else:
      self.lbl_status.foreground = "#666666"

    # Configure action links
    self.link_edit.text = "✏️ Edit"
    self.link_edit.role = "secondary-color"

    self.link_delete.text = "🗑️ Delete"
    self.link_delete.role = "danger"

  @handle("link_edit", "click")
  def link_edit_click(self, **event_args):
    """Edit this room"""
    result = alert(
      content=RoomEditorModal(room_id=self.item.get_id()),
      title="Edit Room",
      large=False,
      buttons=[("Cancel", False), ("Save", True)]
    )

    if result:
      self.parent.raise_event('x-refresh-rooms')

  @handle("link_delete", "click")
  def link_delete_click(self, **event_args):
    """Delete this room"""
    if confirm(f"Delete room {self.item['room_number']}?"):
      try:
        anvil.server.call('delete_room', self.item.get_id())
        Notification("Room deleted successfully").show()
        self.parent.raise_event('x-refresh-rooms')
      except Exception as e:
        alert(f"Error deleting room: {str(e)}")