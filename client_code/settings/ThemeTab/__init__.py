from ._anvil_designer import ThemeTabTemplate
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


class ThemeTab(ThemeTabTemplate):
  """Theme customization tab"""

  def __init__(self, **properties):
    self.init_components(**properties)

    self.lbl_title.text = "Theme Customization"
    self.lbl_title.font_size = 18
    self.lbl_title.bold = True

    # Color pickers (using text input for hex codes)
    self.txt_primary_color.placeholder = "#2196F3"
    self.txt_accent_color.placeholder = "#FF9800"

    # Font family dropdown
    self.dd_font.items = [
      ('Default', 'default'),
      ('Roboto', 'roboto'),
      ('Open Sans', 'open-sans'),
      ('Lato', 'lato'),
      ('Montserrat', 'montserrat')
    ]

    # Header style
    self.dd_header_style.items = [
      ('Light', 'light'),
      ('Dark', 'dark')
    ]

    self.btn_save.text = "Apply Theme"
    self.btn_save.icon = "fa:paint-brush"
    self.btn_save.role = "primary-color"

    self.load_theme()

  def load_theme(self):
    """Load current theme settings"""
    try:
      result = anvil.server.call('get_theme_settings')

      if result['success']:
        theme = result['data']

        self.txt_primary_color.text = theme.get('primary_color', '#2196F3')
        self.txt_accent_color.text = theme.get('accent_color', '#FF9800')
        self.dd_font.selected_value = theme.get('font_family', 'default')
        self.dd_header_style.selected_value = theme.get('header_style', 'light')

    except Exception as e:
      print(f"Error loading theme: {e}")

  def button_save_click(self, **event_args):
    """Save theme settings"""
    try:
      theme_data = {
        'primary_color': self.txt_primary_color.text or '#2196F3',
        'accent_color': self.txt_accent_color.text or '#FF9800',
        'font_family': self.dd_font.selected_value,
        'header_style': self.dd_header_style.selected_value
      }

      result = anvil.server.call('save_theme_settings', theme_data)

      if result['success']:
        Notification("Theme applied successfully!", style="success").show()
        # Refresh page to apply theme
        anvil.js.window.location.reload()
      else:
        alert(f"Error: {result.get('error')}")

    except Exception as e:
      alert(f"Failed to save: {str(e)}")

  @handle("btn_save", "click")
  def btn_save_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
