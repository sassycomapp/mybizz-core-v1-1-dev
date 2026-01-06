from ._anvil_designer import TopResourceTemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class TopResourceTemplate(TopResourceTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    # Display rank with medal
    rank = self.item['rank']
    medals = {1: '🏆', 2: '🥈', 3: '🥉'}
    self.lbl_rank.text = medals.get(rank, f"{rank}.")
    self.lbl_rank.font_size = 20

    # Display resource name
    self.lbl_resource.text = self.item['resource_name']
    self.lbl_resource.bold = True

    # Display booking count
    self.lbl_count.text = f"{self.item['booking_count']} bookings"
    self.lbl_count.foreground = "#666666
