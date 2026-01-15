from ._anvil_designer import CurrencyTabTemplate
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


class CurrencyTab(CurrencyTabTemplate):
  """Currency settings tab"""

  def __init__(self, **properties):
    self.system_currency_locked = False
    self.init_components(**properties)

    self.lbl_title.text = "Currency Settings"
    self.lbl_title.font_size = 18
    self.lbl_title.bold = True

    # Warning text
    self.lbl_warning.text = "⚠️ System currency CANNOT be changed after setup.\n    Display currency is optional for international pricing."
    self.lbl_warning.foreground = "#FF9800"

    # Currency dropdowns
    currencies = [
      ('US Dollar (USD)', 'USD'),
      ('South African Rand (ZAR)', 'ZAR'),
      ('Euro (EUR)', 'EUR'),
      ('British Pound (GBP)', 'GBP'),
      ('Canadian Dollar (CAD)', 'CAD'),
      ('Australian Dollar (AUD)', 'AUD'),
      ('Nigerian Naira (NGN)', 'NGN'),
      ('Kenyan Shilling (KES)', 'KES')
    ]

    self.dd_system_currency.items = currencies
    self.dd_display_currency.items = currencies

    # Display currency toggle
    self.cb_enable_display.text = "Enable Display Currency"

    # Exchange rate
    self.txt_exchange_rate.placeholder = "e.g., 18.50"
    self.txt_exchange_rate.type = "number"

    # Save button
    self.btn_save.text = "Save Currency Settings"
    self.btn_save.icon = "fa:save"
    self.btn_save.role = "primary-color"

    # Load current settings
    self.load_currency_settings()

  def load_currency_settings(self):
    """Load current currency settings"""
    try:
      result = anvil.server.call('get_currency_settings')

      if result['success']:
        settings = result['data']

        # System currency
        system_currency = settings.get('system_currency')
        if system_currency:
          self.dd_system_currency.selected_value = system_currency
          # Lock if already set
          self.system_currency_locked = True
          self.dd_system_currency.enabled = False
          self.lbl_locked.text = "🔒 LOCKED"
          self.lbl_locked.visible = True
        else:
          self.lbl_locked.visible = False

        # Display currency
        display_enabled = settings.get('display_currency_enabled', False)
        self.cb_enable_display.checked = display_enabled

        if display_enabled:
          self.dd_display_currency.selected_value = settings.get('display_currency', 'ZAR')
          self.txt_exchange_rate.text = str(settings.get('exchange_rate', ''))

        self.toggle_display_currency()

    except Exception as e:
      print(f"Error loading currency settings: {e}")

  def toggle_display_currency(self):
    """Show/hide display currency fields"""
    enabled = self.cb_enable_display.checked
    self.dd_display_currency.visible = enabled
    self.txt_exchange_rate.visible = enabled

  def checkbox_enable_display_change(self, **event_args):
    """Toggle display currency fields"""
    self.toggle_display_currency()

  def validate_currency_settings(self):
    """Validate currency settings"""
    if not self.dd_system_currency.selected_value:
      alert("Please select a system currency")
      return False

    if self.cb_enable_display.checked:
      if not self.dd_display_currency.selected_value:
        alert("Please select a display currency")
        return False

      if not self.txt_exchange_rate.text or float(self.txt_exchange_rate.text) <= 0:
        alert("Please enter a valid exchange rate")
        return False

    return True

  def button_save_click(self, **event_args):
    """Save currency settings"""
    if not self.validate_currency_settings():
      return

    try:
      settings = {
        'system_currency': self.dd_system_currency.selected_value,
        'display_currency_enabled': self.cb_enable_display.checked,
        'display_currency': self.dd_display_currency.selected_value if self.cb_enable_display.checked else None,
        'exchange_rate': float(self.txt_exchange_rate.text) if self.cb_enable_display.checked and self.txt_exchange_rate.text else None
      }

      result = anvil.server.call('save_currency_settings', settings, self.system_currency_locked)

      if result['success']:
        Notification("Currency settings saved!", style="success").show()
        self.load_currency_settings()
      else:
        alert(f"Error: {result.get('error')}")

    except Exception as e:
      alert(f"Failed to save: {str(e)}")

  @handle("cb_enable_display", "change")
  def cb_enable_display_change(self, **event_args):
    """This method is called when this checkbox is checked or unchecked"""
    pass

  @handle("btn_save", "click")
  def btn_save_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
