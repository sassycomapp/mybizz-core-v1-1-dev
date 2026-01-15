import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import *
from routing import router

"""
Product UI Helper Functions
Reusable utilities for product package forms
"""



def format_currency(amount, currency='USD'):
  """
  Format number as currency.
  
  Args:
    amount (float): Amount to format
    currency (str): Currency code (default: USD)
    
  Returns:
    str: Formatted currency string
    
  Example:
    >>> format_currency(1234.56)
    '$1,234.56'
  """
  if amount is None:
    return "$0.00"

  if currency == 'USD':
    return f"${amount:,.2f}"
  elif currency == 'EUR':
    return f"€{amount:,.2f}"
  elif currency == 'GBP':
    return f"£{amount:,.2f}"
  else:
    return f"{currency} {amount:,.2f}"

def format_stock_status(quantity):
  """
  Format stock quantity with status indicator.
  
  Args:
    quantity (int): Stock quantity
    
  Returns:
    tuple: (text, color) for display
    
  Example:
    >>> format_stock_status(50)
    ('50', 'green')
  """
  if quantity > 10:
    return (str(quantity), 'green')
  elif quantity > 0:
    return (f"{quantity} (Low)", 'orange')
  else:
    return ("Out of Stock", 'red')

def calculate_discount_percentage(original_price, sale_price):
  """
  Calculate discount percentage.
  
  Args:
    original_price (float): Original price
    sale_price (float): Sale price
    
  Returns:
    int: Discount percentage
    
  Example:
    >>> calculate_discount_percentage(100, 75)
    25
  """
  if not original_price or original_price == 0:
    return 0

  discount = ((original_price - sale_price) / original_price) * 100
  return int(discount)

def validate_product_slug(slug):
  """
  Validate product URL slug format.
  
  Args:
    slug (str): Slug to validate
    
  Returns:
    bool: True if valid
    
  Rules:
    - Lowercase letters, numbers, hyphens only
    - No spaces or special characters
    - Cannot start or end with hyphen
  """
  import re

  if not slug:
    return False

  # Check format
  pattern = r'^[a-z0-9]+(-[a-z0-9]+)*$'
  return bool(re.match(pattern, slug))

def calculate_cart_totals(cart_items, tax_rate=0.10, shipping=0):
  """
  Calculate cart totals.
  
  Args:
    cart_items (list): List of cart item dicts
    tax_rate (float): Tax rate (default: 0.10 = 10%)
    shipping (float): Shipping cost
    
  Returns:
    dict: {'subtotal': float, 'tax': float, 'shipping': float, 'total': float}
    
  Example:
    >>> items = [{'price': 25, 'quantity': 2}, {'price': 10, 'quantity': 1}]
    >>> calculate_cart_totals(items, tax_rate=0.10, shipping=5)
    {'subtotal': 60, 'tax': 6.0, 'shipping': 5, 'total': 71.0}
  """
  subtotal = sum(item.get('price', 0) * item.get('quantity', 1) for item in cart_items)
  tax = subtotal * tax_rate
  total = subtotal + tax + shipping

  return {
    'subtotal': subtotal,
    'tax': tax,
    'shipping': shipping,
    'total': total
  }

def show_product_notification(message, style='info'):
  """
  Show styled notification for product actions.
  
  Args:
    message (str): Notification message
    style (str): 'success', 'warning', 'error', 'info'
    
  Example:
    >>> show_product_notification("Product added to cart!", "success")
  """
  try:
    Notification(message, style=style).show()
  except:
    # Fallback to alert
    alert(message)

def confirm_product_action(action_name, product_name):
  """
  Confirmation dialog for product actions.
  
  Args:
    action_name (str): Action being performed
    product_name (str): Name of product
    
  Returns:
    bool: True if confirmed
    
  Example:
    >>> if confirm_product_action("delete", "T-Shirt"):
    >>>     # Proceed with deletion
  """
  return confirm(f"{action_name.title()} '{product_name}'? This action cannot be undone.")

def generate_product_sku(product_name, variant=None):
  """
  Generate SKU suggestion from product name.
  
  Args:
    product_name (str): Product name
    variant (str): Optional variant name
    
  Returns:
    str: Suggested SKU
    
  Example:
    >>> generate_product_sku("Blue T-Shirt", "Small")
    'BLUE-TSHIRT-SMALL'
  """
  import re

  # Convert to uppercase and remove special characters
  sku = re.sub(r'[^A-Z0-9]+', '-', product_name.upper())
  sku = sku.strip('-')

  if variant:
    variant_sku = re.sub(r'[^A-Z0-9]+', '-', variant.upper())
    sku = f"{sku}-{variant_sku}"

  return sku

def validate_price(price_text):
  """
  Validate and parse price input.
  
  Args:
    price_text (str): Price as string
    
  Returns:
    tuple: (is_valid, price_float, error_message)
    
  Example:
    >>> validate_price("25.99")
    (True, 25.99, None)
    >>> validate_price("-10")
    (False, None, "Price must be positive")
  """
  try:
    price = float(price_text)

    if price < 0:
      return (False, None, "Price must be positive")

    if price > 999999:
      return (False, None, "Price too high")

    return (True, price, None)

  except ValueError:
    return (False, None, "Invalid price format")

def format_order_status(status):
  """
  Format order status with emoji.
  
  Args:
    status (str): Order status
    
  Returns:
    str: Formatted status with emoji
  """
  status_map = {
    'pending': '⏳ Pending',
    'processing': '📦 Processing',
    'shipped': '🚚 Shipped',
    'completed': '✅ Completed',
    'cancelled': '❌ Cancelled',
    'refunded': '💰 Refunded'
  }

  return status_map.get(status, status)

def truncate_description(description, max_length=100):
  """
  Truncate long descriptions with ellipsis.
  
  Args:
    description (str): Full description
    max_length (int): Maximum length
    
  Returns:
    str: Truncated description
  """
  if not description:
    return ""

  if len(description) <= max_length:
    return description

  return description[:max_length] + "..."

def check_inventory_availability(product, quantity):
  """
  Check if product has sufficient inventory.
  
  Args:
    product (dict): Product row
    quantity (int): Requested quantity
    
  Returns:
    tuple: (is_available, message)
    
  Example:
    >>> check_inventory_availability(product_row, 5)
    (True, "In stock")
  """
  if not product.get('track_inventory'):
    return (True, "In stock")

  stock = product.get('inventory_quantity', 0)

  if stock >= quantity:
    return (True, "In stock")
  elif stock > 0:
    return (False, f"Only {stock} available")
  else:
    return (False, "Out of stock")

def calculate_shipping_estimate(items, destination_country='US'):
  """
  Calculate shipping cost estimate.
  
  Args:
    items (list): Cart items
    destination_country (str): Destination country code
    
  Returns:
    float: Estimated shipping cost
    
  Note: This is a simple estimate. Integrate with shipping API for accurate rates.
  """
  # Simple weight-based calculation
  total_weight = sum(
    item.get('product_id', {}).get('weight', 0) * item.get('quantity', 1)
    for item in items
  )

  if destination_country == 'US':
    # Domestic shipping
    if total_weight < 1:
      return 5.00
    elif total_weight < 5:
      return 10.00
    else:
      return 15.00
  else:
    # International shipping
    if total_weight < 1:
      return 15.00
    elif total_weight < 5:
      return 25.00
    else:
      return 40.00

def format_product_images(images, thumbnail_size=100):
  """
  Format product images for display.
  
  Args:
    images (list): List of image media objects or URLs
    thumbnail_size (int): Thumbnail height in pixels
    
  Returns:
    list: Formatted image components
  """
  if not images:
    return []

  formatted = []
  for img in images:
    if img:
      formatted.append({
        'source': img,
        'height': thumbnail_size,
        'clickable': True
      })

  return formatted

def get_product_availability_class(product):
  """
  Get CSS class for product availability.
  
  Args:
    product (dict): Product row
    
  Returns:
    str: CSS class name
  """
  stock = product.get('inventory_quantity', 0)

  if stock > 10:
    return 'in-stock'
  elif stock > 0:
    return 'low-stock'
  else:
    return 'out-of-stock'

# Export all functions
__all__ = [
  'format_currency',
  'format_stock_status',
  'calculate_discount_percentage',
  'validate_product_slug',
  'calculate_cart_totals',
  'show_product_notification',
  'confirm_product_action',
  'generate_product_sku',
  'validate_price',
  'format_order_status',
  'truncate_description',
  'check_inventory_availability',
  'calculate_shipping_estimate',
  'format_product_images',
  'get_product_availability_class'
]
```