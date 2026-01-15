from ._anvil_designer import ClientPortalFormTemplate
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
from datetime import datetime

class ClientPortalForm(ClientPortalFormTemplate):
  def __init__(self, **properties):
    self.current_user = None
    self.init_components(**properties)

    # Check if logged in
    user = anvil.users.get_user()
    if not user:
      open_form('auth.LoginForm')
      return

    self.current_user = user

    # Configure title
    self.lbl_title.text = "My Account"
    self.lbl_title.font_size = 24
    self.lbl_title.bold = True
    self.lbl_title.role = "headline"

    # Configure logout button
    self.btn_logout.text = "Logout"
    self.btn_logout.icon = "fa:sign-out"
    self.btn_logout.role = "secondary-color"

    # Configure welcome
    name = user['email'].split('@')[0]
    self.lbl_welcome.text = f"Welcome back, {name}! 👋"
    self.lbl_welcome.font_size = 18

    # Configure sections
    self.lbl_upcoming_section.text = "UPCOMING APPOINTMENTS"
    self.lbl_upcoming_section.bold = True
    self.lbl_upcoming_section.font_size = 16

    self.lbl_past_section.text = "PAST APPOINTMENTS"
    self.lbl_past_section.bold = True
    self.lbl_past_section.font_size = 16

    self.lbl_invoices_section.text = "INVOICES"
    self.lbl_invoices_section.bold = True
    self.lbl_invoices_section.font_size = 16

    self.lbl_documents_section.text = "SHARED DOCUMENTS"
    self.lbl_documents_section.bold = True
    self.lbl_documents_section.font_size = 16

    # Configure no upcoming label
    self.lbl_no_upcoming.text = "No upcoming appointments"
    self.lbl_no_upcoming.foreground = "#666666"
    self.lbl_no_upcoming.italic = True
    self.lbl_no_upcoming.visible = False

    # Configure book button
    self.btn_book_new.text = "Book New Appointment"
    self.btn_book_new.icon = "fa:calendar-plus"
    self.btn_book_new.role = "primary-color"

    # Set repeating panel templates
    self.rp_upcoming.item_template = 'customers.UpcomingAppointmentTemplate'
    self.rp_past.item_template = 'customers.PastAppointmentTemplate'
    self.rp_invoices.item_template = 'customers.InvoiceTemplate'
    self.rp_documents.item_template = 'customers.DocumentTemplate'

    # Load data
    self.load_portal_data()

  def load_portal_data(self):
    """Load all portal data"""
    try:
      data = anvil.server.call('get_client_portal_data')

      # Upcoming appointments
      if data['upcoming']:
        self.rp_upcoming.items = data['upcoming']
        self.rp_upcoming.visible = True
        self.lbl_no_upcoming.visible = False
      else:
        self.rp_upcoming.visible = False
        self.lbl_no_upcoming.visible = True

      # Past appointments
      self.rp_past.items = data['past'][:5]  # Show last 5

      # Invoices
      self.rp_invoices.items = data['invoices'][:5]

      # Documents
      self.rp_documents.items = data['documents']

    except Exception as e:
      alert(f"Error loading portal data: {str(e)}")

  def button_book_new_click(self, **event_args):
    """Book new appointment"""
    open_form('bookings.PublicBookingWidget')

  def button_logout_click(self, **event_args):
    """Logout"""
    anvil.users.logout()
    open_form('HomePage')

  @handle("btn_book_new", "click")
  def btn_book_new_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_logout", "click")
  def btn_logout_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
