from ._anvil_designer import OrderRowTemplateTemplate
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


class OrderRowTemplate(OrderRowTemplateTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run before the form opens.
class OrderRowTemplate(OrderRowTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    # Display data
    self.lbl_order_number.text = self.item['order_number']
    self.lbl_order_number.bold = True

    self.lbl_customer.text = self.item['customer_email']

    self.lbl_total.text = self.item['total_display']
    self.lbl_total.foreground = "green"

    # Status with color
    status = self.item['status']
    self.lbl_status.text = self.item['status_display']

    if status == 'completed':
      self.lbl_status.foreground = "green"
    elif status in ['pending', 'processing']:
      self.lbl_status.foreground = "orange"
    elif status in ['cancelled', 'refunded']:
      self.lbl_status.foreground = "red"
    else:
      self.lbl_status.foreground = "#666666"

    self.lbl_date.text = self.item['date_display']

    # View link
    self.link_view.text = "View"
    self.link_view.role = "secondary-color"

  def link_view_click(self, **event_args):
    """View order details"""
    result = alert(
      content=OrderDetailModal(order_id=self.item.get_id()),
      title=f"Order {self.item['order_number']}",
      large=True,
      buttons=[("Close", True)]