from ._anvil_designer import RoomEditorModalTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class RoomEditorModal(RoomEditorModalTemplate):
  def __init__(self, room_id=None, **properties):
    self.room_id = room_id
    self.init_components(**properties)

    # Configure labels
    self.lbl_room_number_field.text = "Room Number *"
    self.lbl_room_number_field.bold = True

    self.lbl_type_field.text = "Room Type *"
    self.lbl_type_field.bold = True

    self.lbl_capacity_field.text = "Capacity (guests) *"
    self.lbl_capacity_field.bold = True

    self.lbl_price_field.text = "Price per Night *"
    self.lbl_price_field.bold = True

    self.lbl_status_field.text = "Status"
    self.lbl_status_field.bold = True

    self.lbl_description_field.text = "Description"
    self.lbl_description_field.bold = True

    # Configure fields
    self.txt_room_number.placeholder = "e.g., 101, 102A"

    self.txt_room_type.placeholder = "e.g., Deluxe, Suite, Standard"

    self.txt_capacity.type = "number"
    self.txt_capacity.placeholder = "Number of guests"

    self.txt_price.type = "number"
    self.txt_price.placeholder = "0.00"

    self.dd_status.items = [
      ('Active', 'active'),
      ('Maintenance', 'maintenance'),
      ('Inactive', 'inactive')
    ]
    self.dd_status.selected_value = 'active'

    self.txt_description.placeholder = "Optional description..."
    self.txt_description.rows = 3

    # Load existing room if editing
    if self.room_id:
      self.load_room()

  def load_room(self):
    """Load existing room"""
    try:
      room = anvil.server.call('get_room', self.room_id)
      if room:
        self.txt_room_number.text = room['room_number']
        self.txt_room_type.text = room['room_type']
        self.txt_capacity.text = str(room['capacity'])
        self.txt_price.text = str(room['price_per_night'])
        self.dd_status.selected_value = room['status']
        self.txt_description.text = room.get('description', '')
    except Exception as e:
      alert(f"Error loading room: {str(e)}")

  def save(self):
    """Save room (called when user clicks Save button)"""
    try:
      if not self.txt_room_number.text:
        alert("Room number is required")
        return False

      if not self.txt_room_type.text:
        alert("Room type is required")
        return False

      if not self.txt_capacity.text:
        alert("Capacity is required")
        return False

      if not self.txt_price.text:
        alert("Price is required")
        return False

      room_data = {
        'room_number': self.txt_room_number.text,
        'room_type': self.txt_room_type.text,
        'capacity': int(self.txt_capacity.text),
        'price_per_night': float(self.txt_price.text),
        'status': self.dd_status.selected_value,
        'description': self.txt_description.text
      }

      result = anvil.server.call(
        'save_room',
        self.room_id,
        room_data
      )

      if result['success']:
        return True
      else:
        alert(result['error'])
        return False

    except Exception as e:
      alert(f"Error saving room: {str(e)}")
      return False