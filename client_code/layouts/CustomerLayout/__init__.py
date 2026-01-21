from ._anvil_designer import CustomerLayoutTemplate
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
from routing.router import navigate, get_url_hash

class CustomerLayout(CustomerLayoutTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Configure layout
    self.setup_header()
    self.setup_sidebar()

    # Load user and build navigation
    self.user = anvil.users.get_user()
    if not self.user:
      navigate('/login')
      return

    # Build navigation based on customer's activity
    self.build_navigation()

    # Highlight current page
    self.highlight_current_page()

  def setup_header(self):
    """Configure header panel"""
    self.header_panel.background = "#1976D2"
    self.header_panel.foreground = "#FFFFFF"

    # Logo
    self.lbl_logo.text = "MyBizz"
    self.lbl_logo.font_size = 20
    self.lbl_logo.bold = True
    self.lbl_logo.icon = "fa:user-circle"

    # Load business name
    try:
      config = anvil.server.call('get_config')
      if config and config.get('business_name'):
        self.lbl_logo.text = config['business_name']
    except:
      pass

    # User menu
    user_name = self.user.get('first_name', self.user.get('email', 'User'))
    self.link_user_menu.text = f"👤 {user_name}"
    self.link_user_menu.font_size = 14
    self.link_user_menu.foreground = "#FFFFFF"

  def setup_sidebar(self):
    """Configure sidebar styling"""
    self.sidebar_panel.background = "#FFFFFF"
    self.sidebar_panel.foreground = "#333333"

    # Configure all navigation links
    all_links = [
      self.link_dashboard, self.link_bookings, self.link_orders,
      self.link_membership, self.link_payment_methods, self.link_invoices,
      self.link_reviews, self.link_support, self.link_account
    ]

    for link in all_links:
      link.foreground = "#333333"
      link.role = "sidebar-item"
      link.spacing_above = "none"
      link.spacing_below = "none"

    # Logout link special styling
    self.link_logout.foreground = "#D32F2F"
    self.link_logout.role = "sidebar-item"

  def build_navigation(self):
    """Build navigation based on customer's activity and enabled features"""
    try:
      config = anvil.server.call('get_config')
      features = config.get('features', {}) if config else {}

      # Check customer's activity
      customer_data = anvil.server.call('get_customer_activity', self.user.get_id())

      # --- ALWAYS VISIBLE ---
      self.link_dashboard.text = "📊 My Dashboard"
      self.link_dashboard.visible = True

      self.link_payment_methods.text = "💳 Payment Methods"
      self.link_payment_methods.visible = True

      self.link_invoices.text = "🧾 Invoices"
      self.link_invoices.visible = True

      self.link_support.text = "🎫 Support"
      self.link_support.visible = True

      self.link_account.text = "⚙️ Account Settings"
      self.link_account.visible = True

      self.link_logout.text = "🚪 Logout"
      self.link_logout.visible = True

      # --- CONDITIONAL VISIBILITY ---

      # Bookings - show if customer has bookings OR bookings feature enabled
      has_bookings = customer_data.get('has_bookings', False)
      bookings_enabled = features.get('bookings_enabled', False)
      self.link_bookings.visible = has_bookings or bookings_enabled
      self.link_bookings.text = "📅 My Bookings"

      # Orders - show if customer has orders OR ecommerce enabled
      has_orders = customer_data.get('has_orders', False)
      ecommerce_enabled = features.get('ecommerce_enabled', False)
      self.link_orders.visible = has_orders or ecommerce_enabled
      self.link_orders.text = "📦 My Orders"

      # Membership - show if customer is member OR memberships enabled
      is_member = customer_data.get('is_member', False)
      memberships_enabled = features.get('memberships_enabled', False)
      self.link_membership.visible = is_member or memberships_enabled
      self.link_membership.text = "👥 My Membership"

      # Reviews - show if reviews feature enabled
      reviews_enabled = features.get('reviews_enabled', False)
      self.link_reviews.visible = reviews_enabled
      self.link_reviews.text = "⭐ My Reviews"

    except Exception as e:
      print(f"Error building navigation: {e}")
      # Show all items if error
      for link in [self.link_dashboard, self.link_bookings, self.link_orders,
                   self.link_membership, self.link_payment_methods, 
                   self.link_invoices, self.link_support, self.link_account]:
        link.visible = True

  def highlight_current_page(self):
    """Highlight active menu item based on current route"""
    current_path = get_url_hash()

    # Reset all links
    all_links = [
      self.link_dashboard, self.link_bookings, self.link_orders,
      self.link_membership, self.link_payment_methods, self.link_invoices,
      self.link_reviews, self.link_support, self.link_account
    ]

    for link in all_links:
      link.bold = False
      link.background = "transparent"

    # Highlight current page
    if current_path == "/account" or current_path == "/account/dashboard":
      self.link_dashboard.bold = True
      self.link_dashboard.background = "#E3F2FD"
    elif "/bookings" in current_path:
      self.link_bookings.bold = True
      self.link_bookings.background = "#E3F2FD"
    elif "/orders" in current_path:
      self.link_orders.bold = True
      self.link_orders.background = "#E3F2FD"
    elif "/membership" in current_path:
      self.link_membership.bold = True
      self.link_membership.background = "#E3F2FD"
    elif "/payment-methods" in current_path:
      self.link_payment_methods.bold = True
      self.link_payment_methods.background = "#E3F2FD"
    elif "/invoices" in current_path:
      self.link_invoices.bold = True
      self.link_invoices.background = "#E3F2FD"
    elif "/reviews" in current_path:
      self.link_reviews.bold = True
      self.link_reviews.background = "#E3F2FD"
    elif "/support" in current_path:
      self.link_support.bold = True
      self.link_support.background = "#E3F2FD"
    elif "/settings" in current_path:
      self.link_account.bold = True
      self.link_account.background = "#E3F2FD"

  # --- LOGO CLICK HANDLER ---

  def lbl_logo_click(self, **event_args):
    """Navigate to homepage"""
    navigate("/")

  # --- NAVIGATION CLICK HANDLERS ---

  @handle("link_dashboard", "click")
  def link_dashboard_click(self, **event_args):
    navigate("/account")

  @handle("link_bookings", "click")
  def link_bookings_click(self, **event_args):
    navigate("/account/bookings")

  @handle("link_orders", "click")
  def link_orders_click(self, **event_args):
    navigate("/account/orders")

  @handle("link_membership", "click")
  def link_membership_click(self, **event_args):
    navigate("/account/membership")

  @handle("link_payment_methods", "click")
  def link_payment_methods_click(self, **event_args):
    navigate("/account/payment-methods")

  @handle("link_invoices", "click")
  def link_invoices_click(self, **event_args):
    navigate("/account/invoices")

  @handle("link_reviews", "click")
  def link_reviews_click(self, **event_args):
    navigate("/account/reviews")

  @handle("link_support", "click")
  def link_support_click(self, **event_args):
    navigate("/account/support")

  @handle("link_account", "click")
  def link_account_click(self, **event_args):
    navigate("/account/settings")

  @handle("link_logout", "click")
  def link_logout_click(self, **event_args):
    """Logout and redirect"""
    if confirm("Are you sure you want to logout?"):
      anvil.users.logout()
      navigate("/")

  @handle("link_user_menu", "click")
  def link_user_menu_click(self, **event_args):
    """Navigate to account settings"""
    navigate("/account/settings")