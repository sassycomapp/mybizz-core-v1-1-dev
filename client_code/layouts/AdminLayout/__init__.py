from ._anvil_designer import AdminLayoutTemplate
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

class AdminLayout(AdminLayoutTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Track expanded groups (persisted per user)
    self.expanded_groups = {
      'sales': True,
      'marketing': True,
      'content': True,
      'finance': True,
      'settings': False
    }

    # Configure layout
    self.setup_header()
    self.setup_sidebar()
    self.setup_breadcrumbs()

    # Load user and build navigation
    self.user = anvil.users.get_user()
    if not self.user:
      navigate('/login')
      return

    # Build dynamic navigation
    self.build_navigation()

    # Highlight current page
    self.highlight_current_page()

  def setup_header(self):
    """Configure header panel"""
    self.header_panel.background = "#1976D2"
    self.header_panel.foreground = "#FFFFFF"

    # Logo
    self.lbl_logo.text = "MyBizz Admin"
    self.lbl_logo.font_size = 20
    self.lbl_logo.bold = True
    self.lbl_logo.icon = "fa:dashboard"

    # Notifications
    self.lbl_notifications.text = "🔔"
    self.lbl_notifications.font_size = 18
    self.lbl_notifications.tooltip = "Notifications"

    # User menu
    self.link_user_menu.text = f"👤 {self.user['email'] if self.user else 'User'}"
    self.link_user_menu.font_size = 14

  def setup_sidebar(self):
    """Configure sidebar styling"""
    self.sidebar_panel.background = "#263238"
    self.sidebar_panel.foreground = "#FFFFFF"

    # Configure group headers
    for header in [self.lbl_sales_header, self.lbl_marketing_header, 
                   self.lbl_content_header, self.lbl_finance_header, 
                   self.lbl_settings_header]:
      header.font_size = 12
      header.bold = True
      header.foreground = "#90CAF9"
      header.background = "#37474F"
      header.role = "nav-group-header"
      header.spacing_above = "small"
      header.spacing_below = "none"

    # Configure all navigation links
    all_links = [
      self.link_dashboard, self.link_bookings, self.link_products,
      self.link_orders, self.link_rooms, self.link_services,
      self.link_memberships, self.link_contacts, self.link_campaigns,
      self.link_broadcasts, self.link_segments, self.link_tasks,
      self.link_lead_capture, self.link_referrals, self.link_reviews,
      self.link_blog, self.link_pages, self.link_media,
      self.link_payments, self.link_invoices, self.link_transactions,
      self.link_reports, self.link_business, self.link_branding,
      self.link_features, self.link_users, self.link_integrations,
      self.link_support
    ]

    for link in all_links:
      link.foreground = "#FFFFFF"
      link.role = "sidebar-link"
      link.spacing_above = "none"
      link.spacing_below = "none"

    # Logout link special styling
    self.link_logout.foreground = "#FF5252"
    self.link_logout.role = "sidebar-link"

  def setup_breadcrumbs(self):
    """Configure breadcrumbs panel"""
    self.breadcrumbs_panel.background = "#FFFFFF"
    self.breadcrumbs_panel.spacing_above = "small"
    self.breadcrumbs_panel.spacing_below = "small"

  def build_navigation(self):
    """Build navigation based on user role and enabled features"""
    config = anvil.server.call('get_config')
    features = config.get('features', {}) if config else {}
    user_role = self.user.get('role', 'staff')

    # Configure group headers with expand/collapse icons
    self.lbl_sales_header.text = "▼ Sales & Operations" if self.expanded_groups['sales'] else "▶ Sales & Operations"
    self.lbl_marketing_header.text = "▼ Customers & Marketing" if self.expanded_groups['marketing'] else "▶ Customers & Marketing"
    self.lbl_content_header.text = "▼ Content" if self.expanded_groups['content'] else "▶ Content"
    self.lbl_finance_header.text = "▼ Finance" if self.expanded_groups['finance'] else "▶ Finance"
    self.lbl_settings_header.text = "▼ Settings" if self.expanded_groups['settings'] else "▶ Settings"

    # Show/hide group panels based on expanded state
    self.panel_sales_items.visible = self.expanded_groups['sales']
    self.panel_marketing_items.visible = self.expanded_groups['marketing']
    self.panel_content_items.visible = self.expanded_groups['content']
    self.panel_finance_items.visible = self.expanded_groups['finance']
    self.panel_settings_items.visible = self.expanded_groups['settings']

    # --- SALES & OPERATIONS GROUP ---
    self.link_bookings.visible = features.get('bookings_enabled', False)
    self.link_bookings.text = "📅 Bookings"

    self.link_products.visible = features.get('ecommerce_enabled', False)
    self.link_products.text = "🛍️ Products"

    self.link_orders.visible = features.get('ecommerce_enabled', False)
    self.link_orders.text = "📦 Orders"

    self.link_rooms.visible = features.get('hospitality_enabled', False)
    self.link_rooms.text = "🏨 Rooms"

    self.link_services.visible = features.get('services_enabled', False)
    self.link_services.text = "💼 Services"

    self.link_memberships.visible = features.get('memberships_enabled', False)
    self.link_memberships.text = "👥 Memberships"

    # Hide entire Sales group if no items visible
    has_sales_items = any([
      self.link_bookings.visible,
      self.link_products.visible,
      self.link_orders.visible,
      self.link_rooms.visible,
      self.link_services.visible,
      self.link_memberships.visible
    ])
    self.lbl_sales_header.visible = has_sales_items
    self.panel_sales_items.visible = has_sales_items and self.expanded_groups['sales']

    # --- CUSTOMERS & MARKETING GROUP ---
    self.link_contacts.text = "📇 Contacts"
    self.link_contacts.visible = True  # Always visible (core CRM)

    marketing_enabled = features.get('marketing_enabled', False)
    self.link_campaigns.visible = marketing_enabled
    self.link_campaigns.text = "📧 Campaigns"

    self.link_broadcasts.visible = marketing_enabled
    self.link_broadcasts.text = "📨 Broadcasts"

    self.link_segments.visible = marketing_enabled
    self.link_segments.text = "🎯 Segments"

    self.link_tasks.visible = marketing_enabled
    self.link_tasks.text = "✅ Tasks"

    self.link_lead_capture.visible = marketing_enabled
    self.link_lead_capture.text = "📋 Lead Capture"

    self.link_referrals.visible = features.get('referrals_enabled', False)
    self.link_referrals.text = "🎁 Referrals"

    self.link_reviews.visible = features.get('reviews_enabled', False)
    self.link_reviews.text = "⭐ Reviews"

    # --- CONTENT GROUP ---
    self.link_blog.visible = features.get('blog_enabled', False)
    self.link_blog.text = "📝 Blog"

    self.link_pages.visible = True  # Always visible
    self.link_pages.text = "📄 Pages"

    self.link_media.visible = True  # Always visible
    self.link_media.text = "🖼️ Media"

    # --- FINANCE GROUP (Owner/Manager only) ---
    show_finance = user_role in ['owner', 'manager']
    self.lbl_finance_header.visible = show_finance
    self.panel_finance_items.visible = show_finance and self.expanded_groups['finance']

    if show_finance:
      self.link_payments.text = "💳 Payments"
      self.link_invoices.text = "🧾 Invoices"
      self.link_transactions.text = "💵 Transactions"
      self.link_reports.text = "📊 Reports"

    # --- SETTINGS GROUP (Owner/Manager only) ---
    show_settings = user_role in ['owner', 'manager']
    self.lbl_settings_header.visible = show_settings
    self.panel_settings_items.visible = show_settings and self.expanded_groups['settings']

    if show_settings:
      self.link_business.text = "🏢 Business"
      self.link_branding.text = "🎨 Branding"
      self.link_features.text = "🎛️ Features"
      self.link_users.text = "👤 Users"
      self.link_integrations.text = "🔗 Integrations"

    # --- ALWAYS VISIBLE ---
    self.link_dashboard.text = "📊 Dashboard"
    self.link_support.text = "❓ Support"
    self.link_logout.text = "🚪 Logout"

  def highlight_current_page(self):
    """Highlight active menu item based on current route"""
    current_path = get_url_hash()

    # Reset all links
    all_links = [
      self.link_dashboard, self.link_bookings, self.link_products,
      self.link_orders, self.link_rooms, self.link_services,
      self.link_memberships, self.link_contacts, self.link_campaigns,
      self.link_broadcasts, self.link_segments, self.link_tasks,
      self.link_lead_capture, self.link_referrals, self.link_reviews,
      self.link_blog, self.link_pages, self.link_media,
      self.link_payments, self.link_invoices, self.link_transactions,
      self.link_reports, self.link_business, self.link_branding,
      self.link_features, self.link_users, self.link_integrations,
      self.link_support
    ]

    for link in all_links:
      link.bold = False
      link.background = "transparent"

    # Highlight current page
    if current_path == "/admin" or current_path == "/admin/dashboard":
      self.link_dashboard.bold = True
      self.link_dashboard.background = "#37474F"
    elif "/bookings" in current_path:
      self.link_bookings.bold = True
      self.link_bookings.background = "#37474F"
      self.expanded_groups['sales'] = True
    elif "/products" in current_path:
      self.link_products.bold = True
      self.link_products.background = "#37474F"
      self.expanded_groups['sales'] = True
    elif "/orders" in current_path:
      self.link_orders.bold = True
      self.link_orders.background = "#37474F"
      self.expanded_groups['sales'] = True
    elif "/rooms" in current_path:
      self.link_rooms.bold = True
      self.link_rooms.background = "#37474F"
      self.expanded_groups['sales'] = True
    elif "/services" in current_path:
      self.link_services.bold = True
      self.link_services.background = "#37474F"
      self.expanded_groups['sales'] = True
    elif "/memberships" in current_path or "/members" in current_path:
      self.link_memberships.bold = True
      self.link_memberships.background = "#37474F"
      self.expanded_groups['sales'] = True
    elif "/contacts" in current_path or "/customers" in current_path:
      self.link_contacts.bold = True
      self.link_contacts.background = "#37474F"
      self.expanded_groups['marketing'] = True
    elif "/campaigns" in current_path:
      self.link_campaigns.bold = True
      self.link_campaigns.background = "#37474F"
      self.expanded_groups['marketing'] = True
    elif "/broadcasts" in current_path:
      self.link_broadcasts.bold = True
      self.link_broadcasts.background = "#37474F"
      self.expanded_groups['marketing'] = True
    elif "/segments" in current_path:
      self.link_segments.bold = True
      self.link_segments.background = "#37474F"
      self.expanded_groups['marketing'] = True
    elif "/tasks" in current_path:
      self.link_tasks.bold = True
      self.link_tasks.background = "#37474F"
      self.expanded_groups['marketing'] = True
    elif "/blog" in current_path:
      self.link_blog.bold = True
      self.link_blog.background = "#37474F"
      self.expanded_groups['content'] = True
    elif "/pages" in current_path:
      self.link_pages.bold = True
      self.link_pages.background = "#37474F"
      self.expanded_groups['content'] = True
    elif "/media" in current_path:
      self.link_media.bold = True
      self.link_media.background = "#37474F"
      self.expanded_groups['content'] = True
    elif "/payments" in current_path:
      self.link_payments.bold = True
      self.link_payments.background = "#37474F"
      self.expanded_groups['finance'] = True
    elif "/invoices" in current_path:
      self.link_invoices.bold = True
      self.link_invoices.background = "#37474F"
      self.expanded_groups['finance'] = True
    elif "/reports" in current_path:
      self.link_reports.bold = True
      self.link_reports.background = "#37474F"
      self.expanded_groups['finance'] = True
    elif "/settings" in current_path:
      self.expanded_groups['settings'] = True
      if "/branding" in current_path:
        self.link_branding.bold = True
        self.link_branding.background = "#37474F"
      elif "/features" in current_path:
        self.link_features.bold = True
        self.link_features.background = "#37474F"
      elif "/users" in current_path:
        self.link_users.bold = True
        self.link_users.background = "#37474F"
      elif "/integrations" in current_path:
        self.link_integrations.bold = True
        self.link_integrations.background = "#37474F"
      else:
        self.link_business.bold = True
        self.link_business.background = "#37474F"
  
  def update_breadcrumbs(self):
    """Update breadcrumbs based on current path"""
    current_path = get_url_hash()
    self.breadcrumbs_panel.clear()
    
    # Parse path
    segments = [s for s in current_path.split('/') if s]
    if not segments or segments[0] != 'admin':
      return
    
    # Dashboard link
    home = Link(text="Dashboard", foreground="#1976D2")
    home.set_event_handler('click', lambda **e: navigate("/admin"))
    self.breadcrumbs_panel.add_component(home)
    
    # Add path segments
    for i, segment in enumerate(segments[1:], 1):
      sep = Label(text=" > ", foreground="#999999")
      self.breadcrumbs_panel.add_component(sep)
      
      segment_text = segment.replace('-', ' ').replace('_', ' ').title()
      segment_label = Label(text=segment_text, foreground="#666666")
      self.breadcrumbs_panel.add_component(segment_label)
  
  # --- GROUP HEADER CLICK HANDLERS (Expand/Collapse) ---
  
  def lbl_sales_header_click(self, **event_args):
    """Toggle Sales & Operations group"""
    self.expanded_groups['sales'] = not self.expanded_groups['sales']
    self.panel_sales_items.visible = self.expanded_groups['sales']
    self.lbl_sales_header.text = "▼ Sales & Operations" if self.expanded_groups['sales'] else "▶ Sales & Operations"
  
  def lbl_marketing_header_click(self, **event_args):
    """Toggle Customers & Marketing group"""
    self.expanded_groups['marketing'] = not self.expanded_groups['marketing']
    self.panel_marketing_items.visible = self.expanded_groups['marketing']
    self.lbl_marketing_header.text = "▼ Customers & Marketing" if self.expanded_groups['marketing'] else "▶ Customers & Marketing"
  
  def lbl_content_header_click(self, **event_args):
    """Toggle Content group"""
    self.expanded_groups['content'] = not self.expanded_groups['content']
    self.panel_content_items.visible = self.expanded_groups['content']
    self.lbl_content_header.text = "▼ Content" if self.expanded_groups['content'] else "▶ Content"
  
  def lbl_finance_header_click(self, **event_args):
    """Toggle Finance group"""
    self.expanded_groups['finance'] = not self.expanded_groups['finance']
    self.panel_finance_items.visible = self.expanded_groups['finance']
    self.lbl_finance_header.text = "▼ Finance" if self.expanded_groups['finance'] else "▶ Finance"
  
  def lbl_settings_header_click(self, **event_args):
    """Toggle Settings group"""
    self.expanded_groups['settings'] = not self.expanded_groups['settings']
    self.panel_settings_items.visible = self.expanded_groups['settings']
    self.lbl_settings_header.text = "▼ Settings" if self.expanded_groups['settings'] else "▶ Settings"
  
  # --- NAVIGATION CLICK HANDLERS ---
  
  def link_dashboard_click(self, **event_args):
    navigate("/admin")
  
  def link_bookings_click(self, **event_args):
    navigate("/admin/bookings")
  
  def link_products_click(self, **event_args):
    navigate("/admin/products")
  
  def link_orders_click(self, **event_args):
    navigate("/admin/orders")
  
  def link_rooms_click(self, **event_args):
    navigate("/admin/rooms")
  
  def link_services_click(self, **event_args):
    navigate("/admin/services")
  
  def link_memberships_click(self, **event_args):
    navigate("/admin/memberships")
  
  def link_contacts_click(self, **event_args):
    navigate("/admin/contacts")
  
  def link_campaigns_click(self, **event_args):
    navigate("/admin/campaigns")
  
  def link_broadcasts_click(self, **event_args):
    navigate("/admin/broadcasts")
  
  def link_segments_click(self, **event_args):
    navigate("/admin/segments")
  
  def link_tasks_click(self, **event_args):
    navigate("/admin/tasks")
  
  def link_lead_capture_click(self, **event_args):
    navigate("/admin/lead-capture")
  
  def link_referrals_click(self, **event_args):
    navigate("/admin/referrals")
  
  def link_reviews_click(self, **event_args):
    navigate("/admin/reviews")
  
  def link_blog_click(self, **event_args):
    navigate("/admin/blog")
  
  def link_pages_click(self, **event_args):
    navigate("/admin/pages")
  
  def link_media_click(self, **event_args):
    navigate("/admin/media")
  
  def link_payments_click(self, **event_args):
    navigate("/admin/payments")
  
  def link_invoices_click(self, **event_args):
    navigate("/admin/invoices")
  
  def link_transactions_click(self, **event_args):
    navigate("/admin/transactions")
  
  def link_reports_click(self, **event_args):
    navigate("/admin/reports")
  
  def link_business_click(self, **event_args):
    navigate("/admin/settings")
  
  def link_branding_click(self, **event_args):
    navigate("/admin/settings/branding")
  
  def link_features_click(self, **event_args):
    navigate("/admin/settings/features")
  
  def link_users_click(self, **event_args):
    navigate("/admin/settings/users")
  
  def link_integrations_click(self, **event_args):
    navigate("/admin/settings/integrations")
  
  def link_support_click(self, **event_args):
    navigate("/admin/support")
  
  def link_logout_click(self, **event_args):
    """Logout and redirect"""
    if confirm("Are you sure you want to logout?"):
      anvil.users.logout()
      navigate("/")
  
  def link_user_menu_click(self, **event_args):
    """Show user menu or navigate to profile"""
    navigate("/admin/settings/profile")
```