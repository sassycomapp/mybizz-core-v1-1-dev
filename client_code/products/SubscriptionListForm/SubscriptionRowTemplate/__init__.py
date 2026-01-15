from ._anvil_designer import SubscriptionRowTemplateTemplate
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


class SubscriptionRowTemplate(SubscriptionRowTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    # Display data
    self.lbl_customer.text = self.item['customer_email']
    self.lbl_plan.text = self.item['plan_name']
    self.lbl_amount.text = self.item['amount_display']
    self.lbl_status.text = self.item['status_display']
    self.lbl_next_bill.text = self.item['next_bill_display']

    # Color code status
    if self.item['status'] == 'active':
      self.lbl_status.foreground = "green"
    elif self.item['status'] == 'cancelled':
      self.lbl_status.foreground = "red"
    elif self.item['status'] == 'trial':
      self.lbl_status.foreground = "blue"
    else:
      self.lbl_status.foreground = "orange"

    # Configure manage link
    self.link_manage.text = "Manage"
    self.link_manage.role = "secondary-color"

  def link_manage_click(self, **event_args):
    """Manage subscription"""
    alert("Subscription management coming soon!")