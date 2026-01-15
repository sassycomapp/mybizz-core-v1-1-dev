from ._anvil_designer import OrderDetailModalTemplate
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


class OrderDetailModal(OrderDetailModalTemplate):
  def __init__(self, order_id=None, **properties):
    self.order_id = order_id
    self.init_components(**properties)

    if self.order_id:
      self.load_order()

  def load_order(self):
    """Load order details"""
    try:
      result = anvil.server.call('get_order_details', self.order_id)

      if result['success']:
        order = result['data']

        # Display order info
        self.lbl_order_number.text = order['order_number']
        self.lbl_customer.text = f"Customer: {order['customer_email']}"
        self.lbl_date.text = f"Date: {order['created_at'].strftime('%B %d, %Y at %I:%M %p')}"
        self.lbl_status.text = f"Status: {order['status']}"
        self.lbl_payment_status.text = f"Payment: {order['payment_status']}"

        # Shipping address
        addr = order.get('shipping_address', {})
        address_text = f"{addr.get('address1', '')}\n{addr.get('city', '')}, {addr.get('state', '')} {addr.get('zip', '')}"
        self.lbl_shipping_address.text = address_text

        # Order items
        items = order.get('items', [])
        self.rp_items.items = items

        # Totals
        self.lbl_subtotal.text = f"Subtotal: ${order['subtotal']:.2f}"
        self.lbl_tax.text = f"Tax: ${order['tax']:.2f}"
        self.lbl_shipping.text = f"Shipping: ${order['shipping']:.2f}"
        self.lbl_total.text = f"Total: ${order['total_amount']:.2f}"
        self.lbl_total.bold = True

      else:
        alert(f"Error: {result.get('error', 'Order not found')}")

    except Exception as e:
      print(f"Error loading order: {e}")
      alert(f"Failed to load order: {str(e)}")