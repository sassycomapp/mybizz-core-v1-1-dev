from ._anvil_designer import HomePageTemplate
from .. import startup
from anvil import *
import anvil.server
from routing import router
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class HomePage(HomePageTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    startup.initialize_app_once()
    # Any code you write here will run before the form opens.


# Keep thi at the end of the file:
    _initialized = False
    
    def initialize_app_once():
      global _initialized
      if _initialized:
        return
      _initialized = True
    initialize_app()
