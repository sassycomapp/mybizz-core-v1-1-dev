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
def get_product_by_slug(slug):
  """
  Get product by URL slug.
  
  Args:
    slug (str): Product slug
    
  Returns:
    dict: {'success': bool, 'data': product} or {'success': bool, 'error': str}
  """
  try:
    product = app_tables.products.get(slug=slug, is_active=True)

    if not product:
      return {'success': False, 'error': 'Product not found'}

    return {'success': True, 'data': product}

  except Exception as e:
    print(f"Error getting product by slug: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
@anvil.users.login_required
def get_product(product_id):
  """
  Get single product by ID.
  
  Args:
    product_id (str): Product ID
    
  Returns:
    dict: {'success': bool, 'data': dict} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager', 'staff']:
      return {'success': False, 'error': 'Access denied'}

    product = app_tables.products.get_by_id(product_id)

    if not product:
      return {'success': False, 'error': 'Product not found'}

    return {'success': True, 'data': product}

  except Exception as e:
    print(f"Error getting product: {e}")
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def save_product(product_id, product_data):
  """
  Save or update product.
  
  Args:
    product_id (str): Product ID (None for new)
    product_data (dict): Product fields
    
  Returns:
    dict: {'success': bool, 'product_id': str} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager', 'staff']:
      return {'success': False, 'error': 'Access denied'}

    # Check slug uniqueness
    existing = app_tables.products.get(slug=product_data['slug'])
    if existing and (not product_id or existing.get_id() != product_id):
      return {'success': False, 'error': 'Slug already exists'}

    # Get category
    category = None
    if product_data.get('category_id'):
      category = app_tables.product_categories.get_by_id(product_data['category_id'])

    # Handle images
    images = []
    for img in product_data.get('uploaded_images', []):
      # Upload to Anvil Media
      images.append(img)

    # Prepare row data
    row_data = {
      'name': product_data['name'],
      'slug': product_data['slug'],
      'description': product_data.get('description'),
      'price': product_data['price'],
      'compare_at_price': product_data.get('compare_at_price'),
      'cost': product_data.get('cost'),
      'sku': product_data.get('sku'),
      'inventory_quantity': product_data.get('inventory_quantity', 0),
      'track_inventory': product_data.get('track_inventory', True),
      'allow_backorders': product_data.get('allow_backorders', False),
      'weight': product_data.get('weight'),
      'images': images,
      'category_id': category,
      'is_active': product_data.get('is_active', True),
      'updated_at': datetime.now()
    }

    if product_id:
      # Update existing
      product = app_tables.products.get_by_id(product_id)
      if product:
        product.update(**row_data)
      else:
        return {'success': False, 'error': 'Product not found'}
    else:
      # Create new
      row_data['client_id'] = user
      row_data['created_at'] = datetime.now()
      product = app_tables.products.add_row(**row_data)

    return {'success': True, 'product_id': product.get_id()}

  except Exception as e:

    @anvil.server.callable
@anvil.users.login_required
def get_all_products_filtered(filters):
  """
  Get all products with filters.
  
  Args:
    filters (dict): {'search': str, 'category_id': str, 'stock_filter': str}
    
  Returns:
    dict: {'success': bool, 'data': list} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    # Check permissions
    if user['role'] not in ['owner', 'manager', 'staff']:
      return {'success': False, 'error': 'Access denied'}

    # Build query
    query = {}

    # Category filter
    if filters.get('category_id'):
      category = app_tables.product_categories.get_by_id(filters['category_id'])
      if category:
        query['category_id'] = category

    # Get products
    products = list(app_tables.products.search(
      tables.order_by('created_at', ascending=False),
      **query
    ))

    # Search filter (client-side for simplicity)
    if filters.get('search'):
      search_term = filters['search'].lower()
      products = [
        p for p in products
        if search_term in p['name'].lower() or 
        (p.get('sku') and search_term in p['sku'].lower())
      ]

    # Stock filter
    if filters.get('stock_filter') == 'in_stock':
      products = [p for p in products if p.get('inventory_quantity', 0) > 10]
    elif filters.get('stock_filter') == 'low_stock':
      products = [p for p in products if 0 < p.get('inventory_quantity', 0) <= 10]
    elif filters.get('stock_filter') == 'out_of_stock':
      products = [p for p in products if p.get('inventory_quantity', 0) == 0]

    return {'success': True, 'data': products}

  except Exception as e:
    print(f"Error getting products: {e}")
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def get_all_categories():
  """Get all product categories"""
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager', 'staff']:
      return []

    categories = list(app_tables.product_categories.search(
      is_active=True,
      tables.order_by('sort_order')
    ))

    return categories

  except Exception as e:
    print(f"Error getting categories: {e}")
    return []

@anvil.server.callable
@anvil.users.login_required
def duplicate_product(product_id):
  """
  Duplicate a product.
  
  Args:
    product_id (str): Product to duplicate
    
  Returns:
    dict: {'success': bool, 'product_id': str} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    # Get original product
    original = app_tables.products.get_by_id(product_id)

    if not original:
      return {'success': False, 'error': 'Product not found'}

    # Create duplicate
    new_product = app_tables.products.add_row(
      client_id=user,
      name=f"{original['name']} (Copy)",
      slug=f"{original['slug']}-copy",
      description=original.get('description'),
      short_description=original.get('short_description'),
      price=original['price'],
      compare_at_price=original.get('compare_at_price'),
      cost=original.get('cost'),
      sku=None,  # Don't duplicate SKU
      inventory_quantity=0,  # Start with 0 inventory
      track_inventory=original['track_inventory'],
      allow_backorders=original['allow_backorders'],
      weight=original.get('weight'),
      images=original.get('images'),
      category_id=original.get('category_id'),
      is_active=False,  # Start inactive
      created_at=datetime.now(),
      updated_at=datetime.now()
    )

    return {'success': True, 'product_id': new_product.get_id()}

  except Exception as e:
    print(f"Error duplicating product: {e}")
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def delete_product(product_id):
  """
  Delete a product.
  
  Args:
    product_id (str): Product to delete
    
  Returns:
    dict: {'success': bool} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    # Get product
    product = app_tables.products.get_by_id(product_id)

    if not product:
      return {'success': False, 'error': 'Product not found'}

    # Check if product has orders
    orders = list(app_tables.order_items.search(product_id=product))

    if orders:
      return {'success': False, 'error': 'Cannot delete product with existing orders'}

    # Delete product
    product.delete()

    return {'success': True}

  except Exception as e:
    print(f"Error deleting product: {e}")
    return {'success': False, 'error': str(e)}
    
    print(f"Error saving product: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
def get_public_categories():
  """Get active categories for public"""
  try:
    categories = list(app_tables.product_categories.search(
      is_active=True,
      tables.order_by('sort_order')
    ))

    return categories

  except Exception as e:
    print(f"Error getting categories: {e}")
    return []

@anvil.server.callable
def get_public_products(filters):
  """
  Get products for public catalog.
  
  Args:
    filters (dict): search, category_id, sort, page, per_page
    
  Returns:
    dict: {'success': bool, 'data': {'products': list, 'total_count': int}}
  """
  try:
    # Build query
    query = {'is_active': True}

    # Category filter
    if filters.get('category_id'):
      category = app_tables.product_categories.get_by_id(filters['category_id'])
      if category:
        query['category_id'] = category

    # Get all matching products
    all_products = list(app_tables.products.search(**query))

    # Search filter
    if filters.get('search'):
      search_term = filters['search'].lower()
      all_products = [
        p for p in all_products
        if search_term in p['name'].lower() or 
        (p.get('description') and search_term in p['description'].lower())
      ]

    # Sort
    sort_key = filters.get('sort', 'newest')
    if sort_key == 'newest':
      all_products.sort(key=lambda p: p['created_at'], reverse=True)
    elif sort_key == 'price_asc':
      all_products.sort(key=lambda p: p['price'])
    elif sort_key == 'price_desc':
      all_products.sort(key=lambda p: p['price'], reverse=True)
    elif sort_key == 'name_asc':
      all_products.sort(key=lambda p: p['name'])

    # Pagination
    page = filters.get('page', 1)
    per_page = filters.get('per_page', 20)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    products = all_products[start_idx:end_idx]

    return {
      'success': True,
      'data': {
        'products': products,
        'total_count': len(all_products)
      }
    }

  except Exception as e:
    print(f"Error getting public products: {e}")
    return {'success': False, 'error': str(e)}

@anvil.server.callable
def get_cart_count():
  """Get current cart item count"""
  try:
    # Get or create cart
    user = anvil.users.get_user()

    if user:
      cart = app_tables.cart.get(customer_id=user)
    else:
      # Guest cart (using session)
      # TODO: Implement session-based cart
      return {'count': 0}

    if not cart:
      return {'count': 0}

    # Count items
    items = list(app_tables.cart_items.search(cart_id=cart))
    total_count = sum(item['quantity'] for item in items)

    return {'count': total_count}

  except Exception as e:
    print(f"Error getting cart count: {e}")
    return {'count': 0}

@anvil.server.callable
def add_to_cart(product_id, variant_id, quantity):
  """
  Add product to cart.
  
  Args:
    product_id (str): Product ID
    variant_id (str): Variant ID (optional)
    quantity (int): Quantity to add
    
  Returns:
    dict: {'success': bool} or {'success': bool, 'error': str}
  """
  try:
    # Get product
    product = app_tables.products.get_by_id(product_id)

    if not product or not product['is_active']:
      return {'success': False, 'error': 'Product not available'}

    # Check stock
    if product['track_inventory'] and product['inventory_quantity'] < quantity:
      return {'success': False, 'error': 'Insufficient stock'}

    # Get or create cart
    user = anvil.users.get_user()

    if user:
      cart = app_tables.cart.get(customer_id=user)
      if not cart:
        cart = app_tables.cart.add_row(
          customer_id=user,
          created_at=datetime.now(),
          updated_at=datetime.now()
        )
    else:
      # TODO: Implement guest cart
      return {'success': False, 'error': 'Please login to add to cart'}

    # Check if item already in cart
    variant = None
    if variant_id:
      variant = app_tables.product_variants.get_by_id(variant_id)

    existing_item = app_tables.cart_items.get(
      cart_id=cart,
      product_id=product,
      variant_id=variant
    )

    if existing_item:
      # Update quantity
      existing_item['quantity'] += quantity
      existing_item.update()
    else:
      # Add new item
      app_tables.cart_items.add_row(
        cart_id=cart,
        product_id=product,
        variant_id=variant,
        quantity=quantity,
        price_at_add=product['price'],
        added_at=datetime.now()
      )

    # Update cart timestamp
    cart['updated_at'] = datetime.now()
    cart.update()

    return {'success': True}

  except Exception as e:
    print(f"Error adding to cart: {e}")
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def get_product_variants(product_id):
  """
  Get all variants for a product.
  
  Args:
    product_id (str): Product ID
    
  Returns:
    dict: {'success': bool, 'data': list} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager', 'staff']:
      return {'success': False, 'error': 'Access denied'}

    product = app_tables.products.get_by_id(product_id)

    if not product:
      return {'success': False, 'error': 'Product not found'}

    # Get variants from product_variants table
    variants = list(app_tables.product_variants.search(
      product_id=product,
      tables.order_by('variant_name')
    ))

    return {'success': True, 'data': variants}

  except Exception as e:
    print(f"Error getting variants: {e}")
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def get_variant(variant_id):
  """Get single variant by ID"""
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager', 'staff']:
      return {'success': False, 'error': 'Access denied'}

    variant = app_tables.product_variants.get_by_id(variant_id)

    if not variant:
      return {'success': False, 'error': 'Variant not found'}

    return {'success': True, 'data': variant}

  except Exception as e:
    print(f"Error getting variant: {e}")
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def save_variant(product_id, variant_id, variant_data):
  """
  Save or update variant.
  
  Args:
    product_id (str): Product ID
    variant_id (str): Variant ID (None for new)
    variant_data (dict): Variant fields
    
  Returns:
    dict: {'success': bool} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager', 'staff']:
      return {'success': False, 'error': 'Access denied'}

    product = app_tables.products.get_by_id(product_id)

    if not product:
      return {'success': False, 'error': 'Product not found'}

    row_data = {
      'variant_name': variant_data['variant_name'],
      'sku': variant_data.get('sku'),
      'price_adjustment': variant_data.get('price_adjustment', 0),
      'stock_quantity': variant_data.get('stock_quantity', 0)
    }

    if variant_id:
      # Update existing
      variant = app_tables.product_variants.get_by_id(variant_id)
      if variant:
        variant.update(**row_data)
      else:
        return {'success': False, 'error': 'Variant not found'}
    else:
      # Create new
      row_data['product_id'] = product
      app_tables.product_variants.add_row(**row_data)

    return {'success': True}

  except Exception as e:
    print(f"Error saving variant: {e}")
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def delete_variant(variant_id):
  """Delete variant"""
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    variant = app_tables.product_variants.get_by_id(variant_id)

    if not variant:
      return {'success': False, 'error': 'Variant not found'}

    # Check if variant has orders
    orders = list(app_tables.order_items.search(variant_id=variant))

    if orders:
      return {'success': False, 'error': 'Cannot delete variant with existing orders'}

    variant.delete()

    return {'success': True}

  except Exception as e:
    print(f"Error deleting variant: {e}")
    return {'success': False, 'error': str(e)}

    