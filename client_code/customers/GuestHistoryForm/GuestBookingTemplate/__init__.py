from ._anvil_designer import GuestBookingTemplateTemplate
from anvil import *
from routing import router
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class GuestBookingTemplate(GuestBookingTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    # Format dates
    start = self.item['start_date'].strftime('%b %d')
    end = self.item['end_date'].strftime('%b %d, %Y')

    self.lbl_dates.text = f"{start}-{end}"
    self.lbl_dates.bold = True

    # Details
    nights = self.item['nights']
    room = self.item['room_name']
    amount = self.item['amount']

    self.lbl_details.text = f"•  {room}  •  {nights} nights  •  ${amount:.2f}"

    # Status
    status = self.item['status'].capitalize()
    self.lbl_status.text = status

    if self.item['status'] == 'completed':
      self.lbl_status.foreground = "green"
    elif self.item['status'] == 'checked_in':
      self.lbl_status.foreground = "blue"
    else:
      self.lbl_status.foreground = "#666666"