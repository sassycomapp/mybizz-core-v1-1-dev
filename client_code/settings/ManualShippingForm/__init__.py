from ._anvil_designer import ManualShippingFormTemplate
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


class ManualShippingForm(ManualShippingFormTemplate):
  """Manual shipping entry form"""

  def __init__(self, order_id=None, **properties):
    self.order_id = order_id
    self.init_components(**properties)

    self.lbl_title.text = "Manual Shipping Entry"
    self.lbl_title.font_size = 18
    self.lbl_title.bold = True

    # Order selection
    self.dd_order.placeholder = "Select Order"
    self.load_unshipped_orders()

    if order_id:
      self.dd_order.selected_value = order_id
      self.dd_order.enabled = False

    # Fields
    self.txt_courier.placeholder = "e.g., FedEx, UPS, DHL"
    self.txt_tracking_number.placeholder = "Tracking number"
    self.txt_shipping_cost.placeholder = "0.00"
    self.txt_shipping_cost.type = "number"
    self.txt_tracking_url.placeholder = "https://track.courier.com/..."

    # Button
    self.btn_submit.text = "Mark as Shipped"
    self.btn_submit.icon = "fa:truck"
    self.btn_submit.role = "primary-color"

  def load_unshipped_orders(self):
    """Load orders that haven't been shipped"""
    try:
      result = anvil.server.call('get_unshipped_orders')

      if result['success']:
        orders = result['data']

        items = [
          (f"{order['order_number']} - {order['customer_email']}", order.get_id())
          for order in orders
        ]

        self.dd_order.items = items

    except Exception as e:
      print(f"Error loading orders: {e}")

  def validate_shipment(self):
    """Validate shipment data"""
    if not self.dd_order.selected_value:
      alert("Please select an order")
      return False

    if not self.txt_courier.text:
      alert("Please enter courier name")
      return False

    if not self.txt_tracking_number.text:
      alert("Please enter tracking number")
      return False

    return True

  def button_submit_click(self, **event_args):
    """Submit shipment"""
    if not self.validate_shipment():
      return

    try:
      shipment_data = {
        'order_id': self.dd_order.selected_value or self.order_id,
        'courier_name': self.txt_courier.text,
        'tracking_number': self.txt_tracking_number.text,
        'shipping_cost': float(self.txt_shipping_cost.text) if self.txt_shipping_cost.text else 0,
        'tracking_url': self.txt_tracking_url.text
      }

      result = anvil.server.call('create_manual_shipment', shipment_data)

      if result['success']:
        Notification("Order marked as shipped!", style="success").show()
        self.raise_event('x-close-alert', value=True)
      else:
        alert(f"Error: {result.get('error')}")

    except Exception as e:
      alert(f"Failed: {str(e)}")

  @handle("btn_submit", "click")
  def btn_submit_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
