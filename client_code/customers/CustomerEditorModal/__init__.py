from ._anvil_designer import CustomerEditorModalTemplate
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

class CustomerEditorModal(CustomerEditorModalTemplate):
  def __init__(self, customer_id=None, **properties):
    self.customer_id = customer_id
    self.init_components(**properties)

    # Configure fields
    self.txt_email.placeholder = "email@example.com"
    self.txt_email.type = "email"

    self.dd_role.items = [
      ('Customer', 'customer'),
      ('Staff', 'staff'),
      ('Manager', 'manager')
    ]
    self.dd_role.selected_value = 'customer'

    self.dd_status.items = [
      ('Active', 'active'),
      ('Inactive', 'inactive'),
      ('Suspended', 'suspended')
    ]
    self.dd_status.selected_value = 'active'

    self.txt_phone.placeholder = "Phone number (optional)"

    # Load existing customer
    if self.customer_id:
      self.load_customer()

  def load_customer(self):
    """Load existing customer"""
    try:
      customer = anvil.server.call('get_customer', self.customer_id)
      if customer:
        self.txt_email.text = customer['email']
        self.dd_role.selected_value = customer['role']
        self.dd_status.selected_value = customer['account_status']
        self.txt_phone.text = customer.get('phone', '')
    except Exception as e:
      alert(f"Error loading customer: {str(e)}")

  def save(self):
    """Save customer"""
    try:
      if not self.txt_email.text:
        alert("Email is required")
        return False

      customer_data = {
        'email': self.txt_email.text,
        'role': self.dd_role.selected_value,
        'account_status': self.dd_status.selected_value,
        'phone': self.txt_phone.text
      }

      result = anvil.server.call('save_customer', self.customer_id, customer_data)

      if result['success']:
        return True
      else:
        alert(result['error'])
        return False

    except Exception as e:
      alert(f"Error saving customer: {str(e)}")
      return False