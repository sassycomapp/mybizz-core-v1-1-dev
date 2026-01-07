from ._anvil_designer import TimeSlotTemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class TimeSlotTemplate(TimeSlotTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    # Display time slot
    self.rb_time.text = self.item['time_display']
    self.rb_time.group_name = "timeslots"

  def radiobutton_time_change(self, **event_args):
    """Notify parent when selected"""
    if self.rb_time.selected:
      self.parent.parent.time_slot_selected(self.item['time'])