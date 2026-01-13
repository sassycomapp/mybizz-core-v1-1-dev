from ._anvil_designer import FeaturesTabTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class FeaturesTab(FeaturesTabTemplate):
  """Feature activation tab (Open Verticals)"""

  def __init__(self, **properties):
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "Feature Activation (Open Verticals)"
    self.lbl_title.font_size = 18
    self.lbl_title.bold = True

    # Info text
    self.lbl_info.text = "ℹ️ Activate any features you need. You can enable/disable anytime."
    self.lbl_info.foreground = "#2196F3"

    # Feature checkboxes
    self.cb_bookings.text = "Bookings & Appointments"
    self.lbl_bookings_desc.text = "Accept reservations, schedule appointments, manage calendar"
    self.lbl_bookings_desc.foreground = "#666666"
    self.lbl_bookings_desc.font_size = 12

    self.cb_ecommerce.text = "Product Sales (E-commerce)"
    self.lbl_ecommerce_desc.text = "Sell physical or digital products online"
    self.lbl_ecommerce_desc.foreground = "#666666"
    self.lbl_ecommerce_desc.font_size = 12

    self.cb_subscriptions.text = "Memberships & Subscriptions"
    self.lbl_subs_desc.text = "Recurring billing, member-only content"
    self.lbl_subs_desc.foreground = "#666666"
    self.lbl_subs_desc.font_size = 12

    self.cb_services.text = "Professional Services"
    self.lbl_services_desc.text = "Consulting, therapy, billable hours tracking"
    self.lbl_services_desc.foreground = "#666666"
    self.lbl_services_desc.font_size = 12

    self.cb_hospitality.text = "Hospitality Management"
    self.lbl_hosp_desc.text = "Room bookings, check-in/out, guest management"
    self.lbl_hosp_desc.foreground = "#666666"
    self.lbl_hosp_desc.font_size = 12

    self.cb_blog.text = "Blog & Content"
    self.lbl_blog_desc.text = "Publish blog posts, manage content"
    self.lbl_blog_desc.foreground = "#666666"
    self.lbl_blog_desc.font_size = 12

    # Save button
    self.btn_save.text = "Save Features"
    self.btn_save.icon = "fa:save"
    self.btn_save.role = "primary-color"

    # Load current settings
    self.load_features()

  def load_features(self):
    """Load enabled features"""
    try:
      result = anvil.server.call('get_enabled_features')

      if result['success']:
        features = result['data']

        self.cb_bookings.checked = features.get('bookings', False)
        self.cb_ecommerce.checked = features.get('ecommerce', False)
        self.cb_subscriptions.checked = features.get('subscriptions', False)
        self.cb_services.checked = features.get('services', False)
        self.cb_hospitality.checked = features.get('hospitality', False)
        self.cb_blog.checked = features.get('blog', False)

    except Exception as e:
      print(f"Error loading features: {e}")

  def button_save_click(self, **event_args):
    """Save feature selections"""
    try:
      features = {
        'bookings': self.cb_bookings.checked,
        'ecommerce': self.cb_ecommerce.checked,
        'subscriptions': self.cb_subscriptions.checked,
        'services': self.cb_services.checked,
        'hospitality': self.cb_hospitality.checked,
        'blog': self.cb_blog.checked
      }

      result = anvil.server.call('save_enabled_features', features)

      if result['success']:
        Notification("Features saved successfully!", style="success").show()
      else:
        alert(f"Error: {result.get('error')}")

    except Exception as e:
      alert(f"Failed to save: {str(e)}")

  @handle("btn_save", "click")
  def btn_save_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
