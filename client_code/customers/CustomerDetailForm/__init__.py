from ._anvil_designer import CustomerDetailFormTemplate
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

class CustomerDetailForm(CustomerDetailFormTemplate):
  def __init__(self, customer_id=None, **properties):
    self.customer_id = customer_id
    self.customer = None
    self.current_tab = 'orders'
    self.init_components(**properties)

    # Configure back link
    self.link_back.text = "← Back to Customers"
    self.link_back.role = "secondary-color"

    # Configure title
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True
    self.lbl_title.role = "headline"

    # Configure edit button
    self.btn_edit.text = ""
    self.btn_edit.icon = "fa:pencil"
    self.btn_edit.role = "secondary-color"

    # Configure sections
    self.lbl_info_section.text = "CUSTOMER INFORMATION"
    self.lbl_info_section.bold = True
    self.lbl_info_section.font_size = 16

    self.lbl_summary_section.text = "ACTIVITY SUMMARY"
    self.lbl_summary_section.bold = True
    self.lbl_summary_section.font_size = 16

    self.lbl_activity_section.text = "RECENT ORDERS"
    self.lbl_activity_section.bold = True
    self.lbl_activity_section.font_size = 16

    # Configure no activity label
    self.lbl_no_activity.text = "No activity yet"
    self.lbl_no_activity.align = "center"
    self.lbl_no_activity.foreground = "#666666"
    self.lbl_no_activity.visible = False

    # Set repeating panel template
    self.rp_activity.item_template = 'customers.ActivityItemTemplate'

    # Create tabs
    self.create_tabs()

    # Load customer
    if self.customer_id:
      self.load_customer()

  def create_tabs(self):
    """Create tab buttons"""
    self.fp_tabs.clear()

    tabs = [
      ('📦 Orders', 'orders'),
      ('📅 Bookings', 'bookings'),
      ('🎫 Tickets', 'tickets'),
      ('⭐ Reviews', 'reviews'),
      ('📝 Notes', 'notes')
    ]

    for label, tab_id in tabs:
      btn = Button(
        text=label,
        role="primary-color" if tab_id == self.current_tab else "outlined-button"
      )
      btn.tag = tab_id
      btn.set_event_handler('click', self.tab_clicked)
      self.fp_tabs.add_component(btn)

  def load_customer(self):
    """Load customer details"""
    try:
      data = anvil.server.call('get_customer_details', self.customer_id)

      if not data:
        alert("Customer not found")
        open_form('customers.CustomerListForm')
        return

      self.customer = data['customer']

      # Display info
      self.lbl_title.text = self.customer['email']

      self.lbl_email.text = f"Email: {self.customer['email']}"

      self.lbl_role.text = f"Role: {self.customer['role'].capitalize()}"

      status_text = self.customer['account_status'].capitalize()
      self.lbl_status.text = f"Status: {status_text}"
      if self.customer['account_status'] == 'active':
        self.lbl_status.foreground = "green"

      self.lbl_phone.text = f"Phone: {self.customer.get('phone', 'Not provided')}"

      joined = self.customer['created_at'].strftime('%B %d, %Y') if self.customer.get('created_at') else 'Unknown'
      self.lbl_joined.text = f"Joined: {joined}"

      last_login = self.customer.get('last_login', 'Never')
      if isinstance(last_login, datetime):
        last_login = last_login.strftime('%B %d, %Y at %I:%M %p')
      self.lbl_last_login.text = f"Last Login: {last_login}"

      # Display summary
      summary = data['summary']
      self.lbl_summary.text = (
        f"🛒 Orders: {summary['orders_count']}  •  "
        f"💰 Total Spent: ${summary['total_spent']:.2f}  •  "
        f"📅 Bookings: {summary['bookings_count']}  •  "
        f"🎫 Tickets: {summary['tickets_count']}  •  "
        f"⭐ Reviews: {summary['reviews_count']}"
      )

      # Load initial tab
      self.load_tab_content()

    except Exception as e:
      alert(f"Error loading customer: {str(e)}")

  def load_tab_content(self):
    """Load content for current tab"""
    try:
      if self.current_tab == 'orders':
        self.lbl_activity_section.text = "RECENT ORDERS"
        items = anvil.server.call('get_customer_orders', self.customer_id)
      elif self.current_tab == 'bookings':
        self.lbl_activity_section.text = "BOOKINGS"
        items = anvil.server.call('get_customer_bookings', self.customer_id)
      elif self.current_tab == 'tickets':
        self.lbl_activity_section.text = "SUPPORT TICKETS"
        items = anvil.server.call('get_customer_tickets', self.customer_id)
      elif self.current_tab == 'reviews':
        self.lbl_activity_section.text = "REVIEWS"
        items = anvil.server.call('get_customer_reviews', self.customer_id)
      elif self.current_tab == 'notes':
        self.lbl_activity_section.text = "STAFF NOTES"
        open_form('bookings.ClientNotesForm', customer_id=self.customer_id)
        return

      if items:
        self.rp_activity.items = items
        self.rp_activity.visible = True
        self.lbl_no_activity.visible = False
      else:
        self.rp_activity.visible = False
        self.lbl_no_activity.visible = True

    except Exception as e:
      alert(f"Error loading {self.current_tab}: {str(e)}")

  def tab_clicked(self, sender, **event_args):
    """Handle tab click"""
    self.current_tab = sender.tag

    # Update tab styles
    for btn in self.fp_tabs.get_components():
      if btn.tag == self.current_tab:
        btn.role = "primary-color"
      else:
        btn.role = "outlined-button"

    # Load content
    self.load_tab_content()

  def button_edit_click(self, **event_args):
    """Edit customer"""
    result = alert(
      content=CustomerEditorModal(customer_id=self.customer_id),
      title="Edit Customer",
      large=False,
      buttons=[("Cancel", False), ("Save", True)]
    )

    if result:
      self.load_customer()

  @handle("link_back", "click")
  def link_back_click(self, **event_args):
    """Go back to customer list"""
    open_form('customers.CustomerListForm')

  @handle("btn_edit", "click")
  def btn_edit_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
