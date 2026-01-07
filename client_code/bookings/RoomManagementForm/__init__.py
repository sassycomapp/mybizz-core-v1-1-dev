from ._anvil_designer import RoomManagementFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class RoomManagementForm(RoomManagementFormTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "Room Management"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True
    self.lbl_title.role = "headline"

    # Configure add button
    self.btn_add_room.text = "Add Room"
    self.btn_add_room.icon = "fa:plus"
    self.btn_add_room.role = "primary-color"

    # Configure no rooms label
    self.lbl_no_rooms.text = "No rooms yet. Click 'Add Room' to create one!"
    self.lbl_no_rooms.align = "center"
    self.lbl_no_rooms.foreground = "#666666"
    self.lbl_no_rooms.visible = False

    # Set repeating panel template
    self.rp_rooms.item_template = 'bookings.RoomRowTemplate'

    # Load rooms
    self.load_rooms()

  def load_rooms(self, **event_args):
    """Load all rooms"""
    try:
      rooms = anvil.server.call('get_all_rooms')

      if rooms:
        self.rp_rooms.items = rooms
        self.rp_rooms.visible = True
        self.lbl_no_rooms.visible = False
      else:
        self.rp_rooms.visible = False
        self.lbl_no_rooms.visible = True

    except Exception as e:
      alert(f"Error loading rooms: {str(e)}")

  def button_add_room_click(self, **event_args):
    """Open room editor modal"""
    result = alert(
      content=RoomEditorModal(room_id=None),
      title="Add New Room",
      large=False,
      buttons=[("Cancel", False), ("Save", True)]
    )

    if result:
      self.load_rooms()

  @handle("btn_add_room", "click")
  def btn_add_room_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
