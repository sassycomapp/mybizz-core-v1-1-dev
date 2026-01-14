from ._anvil_designer import NavigationComponentTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class NavigationComponent(NavigationComponentTemplate):
  """Dynamic navigation component based on role and features"""

  def __init__(self, **properties):
    self.init_components(**properties)

    # Get current user
    self.user = anvil.users.get_user()

    # Configure logo
    self.lbl_logo.text = "MyBizz"
    self.lbl_logo.bold = True
    self.lbl_logo.font_size = 18

    # Load navigation items
    self.load_menu_items()

  def load_menu_items(self):
    """Load menu items based on role and enabled features"""
    if not self.user:
      return

    try:
      # Get enabled features
      result = anvil.server.call('get_enabled_features')
      features = result.get('data', {}) if result.get('success') else {}

      role = self.user.get('role', 'customer')

      # Dashboard (all roles)
      self.link_dashboard.text = "Dashboard"
      self.link_dashboard.visible = True

      # Bookings (if feature enabled)
      self.link_bookings.text = "Bookings"
      self.link_bookings.visible = features.get('bookings', False)

      # Products (if feature enabled)
      self.link_products.text = "Products"
      self.link_products.visible = features.get('ecommerce', False)

      # Customers (admin+ only)
      self.link_customers.text = "Customers"
      self.link_customers.visible = role in ['owner', 'manager', 'staff']

      # Settings (owner/manager only)
      self.link_settings.text = "Settings"
      self.link_settings.visible = role in ['owner', 'manager']

      # User menu
      user_name = f"{self.user.get('first_name', '')} {self.user.get('last_name', '')}".strip() or self.user.get('email')
      self.dd_user_menu.items = [
        (user_name, 'profile'),
        ('Logout', 'logout')
      ]

    except Exception as e:
      print(f"Error loading menu: {e}")

  @handle("link_dashboard", "click")
  def link_dashboard_click(self, **event_args):
    """Navigate to dashboard"""
    open_form('dashboard.DashboardForm')

  @handle("link_bookings", "click")
  def link_bookings_click(self, **event_args):
    """Navigate to bookings"""
    open_form('bookings.BookingListForm')

  @handle("link_products", "click")
  def link_products_click(self, **event_args):
    """Navigate to products"""
    open_form('products.ProductListForm')

  @handle("link_customers", "click")
  def link_customers_click(self, **event_args):
    """Navigate to customers"""
    open_form('customers.CustomerListForm')

  @handle("link_settings", "click")
  def link_settings_click(self, **event_args):
    """Navigate to settings"""
    open_form('settings.SettingsForm')

  @handle("dd_user_menu", "change")
  def dd_user_menu_change(self, **event_args):
    """Handle user menu selection"""
    selection = self.dd_user_menu.selected_value

    if selection == 'profile':
      open_form('auth.UserProfileForm')
    elif selection == 'logout':
      anvil.users.logout()
      open_form('auth.LoginForm')