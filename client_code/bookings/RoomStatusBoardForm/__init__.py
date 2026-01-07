from ._anvil_designer import RoomStatusBoardFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class RoomStatusBoardForm(RoomStatusBoardFormTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "Room Status Board"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True
    self.lbl_title.role = "headline"

    # Configure refresh button
    self.btn_refresh.text = "Refresh"
    self.btn_refresh.icon = "fa:refresh"
    self.btn_refresh.role = "secondary-color"

    # Configure legend
    self.lbl_legend.text = "Legend: 🟢 Vacant  🔵 Occupied  🟡 Dirty  🔴 Maintenance"
    self.lbl_legend.font_size = 12
    self.lbl_legend.foreground = "#666666"

    # Configure repeating panel
    self.rp_rooms.item_template = 'bookings.RoomStatusCardTemplate'

    # Configure summary
    self.lbl_summary.font_size = 14
    self.lbl_summary.bold = True

    # Load rooms
    self.load_rooms()

  def load_rooms(self, **event_args):
    """Load all rooms with current status"""
    try:
      rooms = anvil.server.call('get_rooms_with_status')

      if rooms:
        self.rp_rooms.items = rooms
        self.update_summary(rooms)

    except Exception as e:
      alert(f"Error loading rooms: {str(e)}")

  def update_summary(self, rooms):
    """Update summary counts"""
    vacant = len([r for r in rooms if r['display_status'] == 'vacant'])
    occupied = len([r for r in rooms if r['display_status'] == 'occupied'])
    dirty = len([r for r in rooms if r['display_status'] == 'dirty'])
    maintenance = len([r for r in rooms if r['display_status'] == 'maintenance'])

    self.lbl_summary.text = f"Summary: {vacant} Vacant | {occupied} Occupied | {dirty} Dirty | {maintenance} Maintenance"

  def button_refresh_click(self, **event_args):
    """Refresh room status"""
    self.load_rooms()
    Notification("Room status refreshed", style="info").show()

  @handle("btn_refresh", "click")
  def btn_refresh_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
