from ._anvil_designer import SettingsFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class SettingsForm(SettingsFormTemplate):
  """Main settings form with tabbed interface"""

  def __init__(self, **properties):
    self.current_tab = None
    self.init_components(**properties)

    # Check authentication and permissions
    user = anvil.users.get_user()
    if not user:
      open_form('auth.LoginForm')
      return

    if user['role'] not in ['owner', 'manager']:
      alert("Access denied - Settings require owner or manager role")
      open_form('dashboard.DashboardForm')
      return

    # Configure title
    self.lbl_title.text = "⚙️ Settings"
    self.lbl_title.font_size = 24
    self.lbl_title.bold = True

    # Configure close button
    self.btn_close.text = "Close"
    self.btn_close.icon = "fa:times"
    self.btn_close.role = "outlined-button"

    # Configure tab links
    self.link_business_profile.text = "Business Profile"
    self.link_business_profile.font_size = 14

    self.link_features.text = "Features"
    self.link_features.font_size = 14

    self.link_theme.text = "Theme"
    self.link_theme.font_size = 14

    self.link_currency.text = "Currency"
    self.link_currency.font_size = 14

    self.link_users.text = "Users & Permissions"
    self.link_users.font_size = 14

    # Show first tab by default
    self.show_tab('business_profile')

  def show_tab(self, tab_name):
    """Display selected tab content"""
    # Clear current content
    self.col_content.clear()

    # Reset all tab styles
    for link in [self.link_business_profile, self.link_features, 
                 self.link_theme, self.link_currency, self.link_users]:
      link.bold = False
      link.foreground = "#666666"

    # Highlight active tab
    self.current_tab = tab_name

    # Load appropriate tab content
    if tab_name == 'business_profile':
      self.link_business_profile.bold = True
      self.link_business_profile.foreground = "#2196F3"

      from .BusinessProfileTab import BusinessProfileTab
      tab_component = BusinessProfileTab()
      self.col_content.add_component(tab_component)

    elif tab_name == 'features':
      self.link_features.bold = True
      self.link_features.foreground = "#2196F3"

      from .FeaturesTab import FeaturesTab
      tab_component = FeaturesTab()
      self.col_content.add_component(tab_component)

    elif tab_name == 'theme':
      self.link_theme.bold = True
      self.link_theme.foreground = "#2196F3"

      from .ThemeTab import ThemeTab
      tab_component = ThemeTab()
      self.col_content.add_component(tab_component)

    elif tab_name == 'currency':
      self.link_currency.bold = True
      self.link_currency.foreground = "#2196F3"

      from .CurrencyTab import CurrencyTab
      tab_component = CurrencyTab()
      self.col_content.add_component(tab_component)

    elif tab_name == 'users':
      self.link_users.bold = True
      self.link_users.foreground = "#2196F3"

      from .UsersTab import UsersTab
      tab_component = UsersTab()
      self.col_content.add_component(tab_component)

  @handle("link_business_profile", "click")
  def link_business_profile_click(self, **event_args):
    """Show Business Profile tab"""
    self.show_tab('business_profile')

  @handle("link_features", "click")
  def link_features_click(self, **event_args):
    """Show Features tab"""
    self.show_tab('features')

  @handle("link_theme", "click")
  def link_theme_click(self, **event_args):
    """Show Theme tab"""
    self.show_tab('theme')

  @handle("link_currency", "click")
  def link_currency_click(self, **event_args):
    """Show Currency tab"""
    self.show_tab('currency')

  @handle("link_users", "click")
  def link_users_click(self, **event_args):
    """Show Users tab"""
    self.show_tab('users')

  def button_close_click(self, **event_args):
    """Close settings and return to dashboard"""
    open_form('dashboard.DashboardForm')

  @handle("btn_close", "click")
  def btn_close_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
