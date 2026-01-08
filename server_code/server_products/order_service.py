import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.stripe
import anvil.secrets
import anvil.files
from anvil.files import data_files
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
from datetime import datetime

@anvil.server.callable
@anvil.users.login_required
def create_order_from_cart(customer_data, shipping_data, payment_method):
  """
  Create order from cart and process payment.
  
  Args:
    customer_data (dict): Customer contact info
    shipping_data (dict): Shipping address
    payment_method (str): 'stripe' or 'paystack'
    
  Returns:
    dict: {'success': bool, 'order_number': str} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    # Get cart
    cart = app_tables.cart.get(customer_id=user)

    if not cart:
      return {'success': False, 'error': 'Cart is empty'}

    cart_items = list(app_tables.cart_items.search(cart_id=cart))

    if not cart_items:
      return {'success': False, 'error': 'Cart is empty'}

    # Calculate totals
    subtotal = sum(item['price_at_add'] * item['quantity'] for item in cart_items)
    tax = subtotal * 0.10
    shipping_cost = 5.00
    total = subtotal + tax + shipping_cost

    # Generate order number
    order_number = generate_order_number()

    # Create order
    order = app_tables.orders.add_row(
      order_number=order_number,
      client_id=user,  # Business owner (for multi-tenant)
      customer_id=user,
      status='pending',
      payment_status='unpaid',
      subtotal=subtotal,
      tax=tax,
      shipping=shipping_cost,
      discount=0,
      total_amount=total,
      shipping_address=shipping_data,
      billing_address=shipping_data,  # Same as shipping for now
      notes=None,
      created_at=datetime.now(),
      updated_at=datetime.now()
    )

    # Create order items
    for item in cart_items:
      app_tables.order_items.add_row(
        order_id=order,
        product_id=item['product_id'],
        product_name=item['product_id']['name'],
        quantity=item['quantity'],
        price=item['price_at_add'],
        subtotal=item['price_at_add'] * item['quantity']
      )

      # Deduct inventory
      product = item['product_id']
      if product['track_inventory']:
        product['inventory_quantity'] -= item['quantity']
        product.update()

    # Clear cart
    for item in cart_items:
      item.delete()

    # TODO: Process payment with gateway
    # For now, mark as pending

    return {'success': True, 'order_number': order_number}

  except Exception as e:
    print(f"Error creating order: {e}")
    return {'success': False, 'error': str(e)}

def generate_order_number():
  """Generate unique order number"""
  from datetime import datetime

  date_str = datetime.now().strftime('%Y%m%d')

  # Count orders today
  today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
  today_orders = len(list(app_tables.orders.search(
    created_at=q.greater_than_or_equal_to(today_start)
  )))

  sequence = today_orders + 1

  return f"ORD-{date_str}-{sequence:03d}"