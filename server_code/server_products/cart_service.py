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
def get_cart():
  """
  Get current user's cart.
  
  Returns:
    dict: {'success': bool, 'data': list} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if not user:
      return {'success': False, 'error': 'Login required'}

    # Get cart
    cart = app_tables.cart.get(customer_id=user)

    if not cart:
      return {'success': True, 'data': []}

    # Get cart items with product details
    cart_items = list(app_tables.cart_items.search(
      cart_id=cart,
      tables.order_by('added_at', ascending=False)
    ))

    # Calculate subtotals
    for item in cart_items:
      item['subtotal'] = item['price_at_add'] * item['quantity']

    return {'success': True, 'data': cart_items}

  except Exception as e:
    print(f"Error getting cart: {e}")
    return {'success': False, 'error': str(e)}

@anvil.server.callable
def update_cart_quantity(cart_item_id, new_quantity):
  """
  Update cart item quantity.
  
  Args:
    cart_item_id (str): Cart item ID
    new_quantity (int): New quantity
    
  Returns:
    dict: {'success': bool} or {'success': bool, 'error': str}
  """
  try:
    if new_quantity < 1:
      return {'success': False, 'error': 'Quantity must be at least 1'}

    cart_item = app_tables.cart_items.get_by_id(cart_item_id)

    if not cart_item:
      return {'success': False, 'error': 'Item not found'}

    # Check stock
    product = cart_item['product_id']
    if product['track_inventory'] and product['inventory_quantity'] < new_quantity:
      return {'success': False, 'error': f'Only {product["inventory_quantity"]} available'}

    # Update quantity
    cart_item['quantity'] = new_quantity
    cart_item.update()

    # Update cart timestamp
    cart = cart_item['cart_id']
    cart['updated_at'] = datetime.now()
    cart.update()

    return {'success': True}

  except Exception as e:
    print(f"Error updating cart quantity: {e}")
    return {'success': False, 'error': str(e)}

@anvil.server.callable
def remove_cart_item(cart_item_id):
  """
  Remove item from cart.
  
  Args:
    cart_item_id (str): Cart item ID
    
  Returns:
    dict: {'success': bool} or {'success': bool, 'error': str}
  """
  try:
    cart_item = app_tables.cart_items.get_by_id(cart_item_id)

    if not cart_item:
      return {'success': False, 'error': 'Item not found'}

    cart = cart_item['cart_id']
    cart_item.delete()

    # Update cart timestamp
    cart['updated_at'] = datetime.now()
    cart.update()

    return {'success': True}

  except Exception as e:
    print(f"Error removing cart item: {e}")
    return {'success': False, 'error': str(e)}

@anvil.server.callable
def clear_cart():
  """Clear current user's cart"""
  try:
    user = anvil.users.get_user()

    if not user:
      return {'success': False, 'error': 'Login required'}

    cart = app_tables.cart.get(customer_id=user)

    if cart:
      # Delete all items
      items = list(app_tables.cart_items.search(cart_id=cart))
      for item in items:
        item.delete()

    return {'success': True}

  except Exception as e:
    print(f"Error clearing cart: {e}")
    return {'success': False, 'error': str(e)}