from ._anvil_designer import ActivityItemTemplateTemplate
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


    # Any code you write here will run before the form opens.
class ActivityItemTemplate(ActivityItemTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    # Display activity
    icon = self.item.get('icon', '•')
    description = self.item.get('description', '')
    time_ago = self.item.get('time_ago', '')

    self.lbl_activity.text = f"{icon} {description} - {time_ago}"
    self.lbl_activity.font_size = 14
    self.lbl_activity.spacing_above = 'small'
    self.lbl_activity.spacing_below = 'small'