from ._anvil_designer import PastAppointmentTemplateTemplate
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


class PastAppointmentTemplate(PastAppointmentTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    date_str = self.item['datetime'].strftime('%b %d, %Y')
    self.lbl_info.text = f"{date_str} - {self.item['service_name']} - {self.item['status'].capitalize()}"