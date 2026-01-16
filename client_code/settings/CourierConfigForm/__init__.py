from ._anvil_designer import CourierConfigFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class CourierConfigForm(CourierConfigFormTemplate):
  """Courier API configuration form"""

  def __init__(self, **properties):
    self.init_components(**properties)

    self.lbl_title.text = "Courier API Configuration"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True

    # South African courier
    self.lbl_sa_courier.text = "South African Courier"
    self.lbl_sa_courier.font_size = 16
    self.lbl_sa_courier.bold = True

    self.dd_sa_provider.items = [
      ('Select Provider', None),
      ('Bob Go', 'bobgo')
    ]

    self.txt_sa_api_key.placeholder = "API Key"
    self.txt_sa_api_key.type = "password"

    self.cb_sa_enabled.text = "Enable South African Courier"

    # International courier
    self.lbl_int_courier.text = "International Courier"
    self.lbl_int_courier.font_size = 16
    self.lbl_int_courier.bold = True

    self.dd_int_provider.items = [
      ('Select Provider', None),
      ('Easyship', 'easyship')
    ]

    self.txt_int_api_key.placeholder = "API Key"
    self.txt_int_api_key.type = "password"

    self.cb_int_enabled.text = "Enable International Courier"

    # Save button
    self.btn_save.text = "Save Configuration"
    self.btn_save.icon = "fa:save"
    self.btn_save.role = "primary-color"

    # Load current config
    self.load_config()

  def load_config(self):
    """Load current courier configuration"""
    try:
      result = anvil.server.call('get_courier_config')

      if result['success']:
        config = result['data']

        # SA courier
        if config.get('sa_provider'):
          self.dd_sa_provider.selected_value = config['sa_provider']
        if config.get('sa_api_key'):
          self.txt_sa_api_key.text = "••••••••"  # Masked
        self.cb_sa_enabled.checked = config.get('sa_enabled', False)

        # International courier
        if config.get('int_provider'):
          self.dd_int_provider.selected_value = config['int_provider']
        if config.get('int_api_key'):
          self.txt_int_api_key.text = "••••••••"  # Masked
        self.cb_int_enabled.checked = config.get('int_enabled', False)

    except Exception as e:
      print(f"Error loading config: {e}")

  def button_save_click(self, **event_args):
    """Save courier configuration"""
    try:
      config_data = {
        'sa_provider': self.dd_sa_provider.selected_value,
        'sa_api_key': self.txt_sa_api_key.text if self.txt_sa_api_key.text != "••••••••" else None,
        'sa_enabled': self.cb_sa_enabled.checked,
        'int_provider': self.dd_int_provider.selected_value,
        'int_api_key': self.txt_int_api_key.text if self.txt_int_api_key.text != "••••••••" else None,
        'int_enabled': self.cb_int_enabled.checked
      }

      result = anvil.server.call('save_courier_config', config_data)

      if result['success']:
        Notification("Courier configuration saved!", style="success").show()
      else:
        alert(f"Error: {result.get('error')}")

    except Exception as e:
      alert(f"Failed to save: {str(e)}")

  @handle("btn_save", "click")
  def btn_save_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
