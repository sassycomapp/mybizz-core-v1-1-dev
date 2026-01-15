from ._anvil_designer import CustomerListFormTemplate
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

class CustomerListForm(CustomerListFormTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "Customers"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True
    self.lbl_title.role = "headline"

    # Configure add button
    self.btn_add.text = "Add Customer"
    self.btn_add.icon = "fa:plus"
    self.btn_add.role = "primary-color"

    # Configure search
    self.txt_search.placeholder = "Search by name or email..."
    self.txt_search.icon = "fa:search"

    self.btn_search.text = ""
    self.btn_search.icon = "fa:search"
    self.btn_search.role = "secondary-color"

    # Configure filters
    self.dd_role_filter.items = [
      ('All Roles', 'all'),
      ('Customer', 'customer'),
      ('Staff', 'staff'),
      ('Manager', 'manager')
    ]
    self.dd_role_filter.selected_value = 'all'

    self.dd_status_filter.items = [
      ('All Statuses', 'all'),
      ('Active', 'active'),
      ('Inactive', 'inactive'),
      ('Suspended', 'suspended')
    ]
    self.dd_status_filter.selected_value = 'all'

    # Configure data grid
    self.dg_customers.columns = [
      {'id': 'email', 'title': 'Name/Email', 'data_key': 'email', 'width': 200},
      {'id': 'role', 'title': 'Role', 'data_key': 'role', 'width': 100},
      {'id': 'status', 'title': 'Status', 'data_key': 'account_status', 'width': 100},
      {'id': 'joined', 'title': 'Joined', 'data_key': 'joined_date', 'width': 120},
      {'id': 'actions', 'title': 'Actions', 'data_key': None, 'width': 120}
    ]

    # Configure stats
    self.lbl_stats.font_size = 12
    self.lbl_stats.foreground = "#666666"

    # Load customers
    self.load_customers()

  def load_customers(self):
    """Load customers with filters"""
    try:
      filters = {
        'search': self.txt_search.text,
        'role': self.dd_role_filter.selected_value if self.dd_role_filter.selected_value != 'all' else None,
        'status': self.dd_status_filter.selected_value if self.dd_status_filter.selected_value != 'all' else None
      }

      customers = anvil.server.call('get_all_customers_filtered', filters)

      # Add display fields
      for customer in customers:
        customer['joined_date'] = customer['created_at'].strftime('%b %d, %Y') if customer.get('created_at') else 'N/A'

      self.dg_customers.items = customers

      # Update stats
      total = len(customers)
      active = len([c for c in customers if c['account_status'] == 'active'])
      inactive = len([c for c in customers if c['account_status'] == 'inactive'])

      self.lbl_stats.text = f"Total: {total} customers  •  Active: {active}  •  Inactive: {inactive}"

    except Exception as e:
      alert(f"Error loading customers: {str(e)}")

  def button_add_click(self, **event_args):
    """Add new customer"""
    result = alert(
      content=CustomerEditorModal(customer_id=None),
      title="Add New Customer",
      large=False,
      buttons=[("Cancel", False), ("Save", True)]
    )

    if result:
      self.load_customers()

  def button_search_click(self, **event_args):
    """Search customers"""
    self.load_customers()

  def dropdown_role_filter_change(self, **event_args):
    """Filter by role"""
    self.load_customers()

  def dropdown_status_filter_change(self, **event_args):
    """Filter by status"""
    self.load_customers()

  @handle("btn_add", "click")
  def btn_add_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_search", "click")
  def btn_search_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("dd_role_filter", "change")
  def dd_role_filter_change(self, **event_args):
    """This method is called when an item is selected"""
    pass

  @handle("dd_status_filter", "change")
  def dd_status_filter_change(self, **event_args):
    """This method is called when an item is selected"""
    pass
