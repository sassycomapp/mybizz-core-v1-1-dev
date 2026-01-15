from ._anvil_designer import DashboardFormTemplate
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


class DashboardForm(DashboardFormTemplate):
  """Main dashboard landing page after login"""

  def __init__(self, **properties):
    self.current_user = None
    self.init_components(**properties)

    # Check authentication
    user = anvil.users.get_user()
    if not user:
      # Not logged in - redirect to login
      open_form('auth.LoginForm')
      return

    self.current_user = user

    # Configure header
    self.col_header.background = "#2196F3"
    self.col_header.foreground = "white"

    self.link_menu.text = "☰"
    self.link_menu.font_size = 24
    self.link_menu.foreground = "white"

    self.lbl_app_name.text = "MyBizz"
    self.lbl_app_name.font_size = 20
    self.lbl_app_name.bold = True

    # User info
    user_email = user['email'].split('@')[0]
    self.lbl_user_name.text = f"👤 {user_email}"
    self.lbl_user_name.foreground = "white"

    self.btn_logout.text = "Logout"
    self.btn_logout.role = "outlined-button"
    self.btn_logout.foreground = "white"

    # Configure sidebar
    self.col_sidebar.background = "white"
    self.load_navigation()

    # Configure content area
    self.lbl_page_title.text = "Dashboard Overview"
    self.lbl_page_title.font_size = 24
    self.lbl_page_title.bold = True

    # Load dashboard components
    self.load_dashboard_components()

  def load_navigation(self):
    """Load navigation menu based on user role"""
    try:
      # Get user role
      role = self.current_user.get('role', 'customer')

      # Define menu items
      menu_items = [
        {'icon': '📊', 'text': 'Dashboard', 'form': 'dashboard.DashboardForm', 'roles': ['owner', 'manager', 'staff']},
        {'icon': '📅', 'text': 'Bookings', 'form': 'bookings.BookingListForm', 'roles': ['owner', 'manager', 'staff']},
        {'icon': '🛒', 'text': 'Products', 'form': 'products.ProductListForm', 'roles': ['owner', 'manager', 'staff']},
        {'icon': '👥', 'text': 'Customers', 'form': 'customers.CustomerListForm', 'roles': ['owner', 'manager']},
        {'icon': '✍️', 'text': 'Blog', 'form': 'blog.BlogListForm', 'roles': ['owner', 'manager']},
        {'icon': '📊', 'text': 'Analytics', 'form': 'analytics.AnalyticsForm', 'roles': ['owner', 'manager']},
        {'icon': '⚙️', 'text': 'Settings', 'form': 'settings.SettingsForm', 'roles': ['owner', 'manager']},
      ]

      # Filter by role and add to sidebar
      for item in menu_items:
        if role in item['roles']:
          nav_link = Link(
            text=f"{item['icon']} {item['text']}",
            font_size=14,
            spacing_above='small',
            spacing_below='small'
          )
          nav_link.tag = item['form']
          nav_link.set_event_handler('click', self.nav_link_click)
          self.col_sidebar.add_component(nav_link)

    except Exception as e:
      print(f"Error loading navigation: {e}")

  def load_dashboard_components(self):
    """Load metrics, activity, and storage widgets"""
    try:
      # Add MetricsPanel
      from .MetricsPanel import MetricsPanel
      metrics_panel = MetricsPanel()
      self.col_metrics.add_component(metrics_panel)

      # Add ActivityFeed
      from .ActivityFeed import ActivityFeed
      activity_feed = ActivityFeed()
      self.col_activity.add_component(activity_feed)

      # Add StorageWidget
      from .StorageWidget import StorageWidget
      storage_widget = StorageWidget()
      self.col_storage.add_component(storage_widget)

    except Exception as e:
      print(f"Error loading dashboard components: {e}")
      alert(f"Some dashboard components failed to load: {str(e)}")

  def nav_link_click(self, sender, **event_args):
    """Navigate to selected form"""
    form_path = sender.tag
    if form_path:
      try:
        # Parse package and form name
        parts = form_path.split('.')
        if len(parts) == 2:
          package, form_name = parts
          # Dynamic import
          module = __import__(f'..{package}.{form_name}', fromlist=[form_name], level=1)
          form_class = getattr(module, form_name)
          open_form(form_class())
      except Exception as e:
        print(f"Navigation error: {e}")
        alert(f"Could not open {form_path}")

  @handle("link_menu", "click")
  def link_menu_click(self, **event_args):
    """Toggle sidebar visibility"""
    self.col_sidebar.visible = not self.col_sidebar.visible

  def button_logout_click(self, **event_args):
    """Logout user"""
    if confirm("Are you sure you want to logout?"):
      anvil.users.logout()
      open_form('auth.LoginForm')

  @handle("btn_logout", "click")
  def btn_logout_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
      