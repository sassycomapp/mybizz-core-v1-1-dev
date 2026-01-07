from ._anvil_designer import CustomerRowTemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class CustomerRowTemplate(CustomerRowTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    # Display data
    self.lbl_email.text = self.item['email']

    self.lbl_role.text = self.item['role'].capitalize()

    # Status with color
    status_text = self.item['account_status'].capitalize()
    self.lbl_status.text = status_text

    if self.item['account_status'] == 'active':
      self.lbl_status.foreground = "green"
    elif self.item['account_status'] == 'inactive':
      self.lbl_status.foreground = "#999999"
    else:
      self.lbl_status.foreground = "red"

    self.lbl_joined.text = self.item['joined_date']

    # Configure links
    self.link_view.text = "View"
    self.link_view.role = "secondary-color"

    self.link_edit.text = "Edit"
    self.link_edit.role = "secondary-color"

  def link_view_click(self, **event_args):
    """View customer details"""
    open_form('customers.CustomerDetailForm', customer_id=self.item.get_id())

  def link_edit_click(self, **event_args):
    """Edit customer"""
    result = alert(
      content=CustomerEditorModal(customer_id=self.item.get_id()),
      title="Edit Customer",
      large=False,
      buttons=[("Cancel", False), ("Save", True)]
    )

    if result:
      self.parent.parent.load_customers()