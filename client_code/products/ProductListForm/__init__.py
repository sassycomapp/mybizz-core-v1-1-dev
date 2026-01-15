from ._anvil_designer import ProductListFormTemplate
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


class ProductListForm(ProductListFormTemplate):
  """Admin product management - list all products"""

  def __init__(self, **properties):
    self.init_components(**properties)

    # Check authentication and permissions
    user = anvil.users.get_user()
    if not user:
      open_form('auth.LoginForm')
      return

    if user['role'] not in ['owner', 'manager', 'staff']:
      alert("Access denied")
      open_form('dashboard.DashboardForm')
      return

    # Configure title
    self.lbl_title.text = "Products"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True
    self.lbl_title.role = "headline"

    # Configure add button
    self.btn_add.text = "Add Product"
    self.btn_add.icon = "fa:plus"
    self.btn_add.role = "primary-color"

    # Configure search
    self.txt_search.placeholder = "Search by name or SKU..."
    self.txt_search.icon = "fa:search"

    self.btn_search.text = ""
    self.btn_search.icon = "fa:search"
    self.btn_search.role = "secondary-color"

    # Configure filters
    self.dd_category_filter.items = [('All Categories', None)]
    self.load_categories()

    self.dd_stock_filter.items = [
      ('All Stock Levels', 'all'),
      ('In Stock', 'in_stock'),
      ('Low Stock', 'low_stock'),
      ('Out of Stock', 'out_of_stock')
    ]
    self.dd_stock_filter.selected_value = 'all'

    # Configure data grid
    self.dg_products.columns = [
      {'id': 'image', 'title': '📷', 'data_key': 'image', 'width': 80},
      {'id': 'name', 'title': 'Name', 'data_key': 'name', 'width': 200},
      {'id': 'price', 'title': 'Price', 'data_key': 'price_display', 'width': 100},
      {'id': 'stock', 'title': 'Stock', 'data_key': 'stock_display', 'width': 100},
      {'id': 'status', 'title': 'Status', 'data_key': 'status_display', 'width': 100},
      {'id': 'actions', 'title': 'Actions', 'data_key': None, 'width': 150}
    ]

    # Configure stats
    self.lbl_stats.font_size = 12
    self.lbl_stats.foreground = "#666666"

    # Load products
    self.load_products()

  def load_categories(self):
    """Load categories for filter dropdown"""
    try:
      categories = anvil.server.call('get_all_categories')

      items = [('All Categories', None)]
      for cat in categories:
        items.append((cat['name'], cat.get_id()))

      self.dd_category_filter.items = items

    except Exception as e:
      print(f"Error loading categories: {e}")

  def load_products(self):
    """Load products with filters"""
    try:
      filters = {
        'search': self.txt_search.text,
        'category_id': self.dd_category_filter.selected_value,
        'stock_filter': self.dd_stock_filter.selected_value
      }

      result = anvil.server.call('get_all_products_filtered', filters)

      if result['success']:
        products = result['data']

        # Add display fields
        for product in products:
          # Price display
          product['price_display'] = f"${product['price']:.2f}"

          # Stock display
          stock = product.get('inventory_quantity', 0)
          if stock > 10:
            product['stock_display'] = str(stock)
          elif stock > 0:
            product['stock_display'] = f"{stock} (Low)"
          else:
            product['stock_display'] = "Out of Stock"

          # Status display
          product['status_display'] = "Active" if product.get('is_active') else "Inactive"

        self.dg_products.items = products

        # Update stats
        total = len(products)
        active = len([p for p in products if p.get('is_active')])
        out_of_stock = len([p for p in products if p.get('inventory_quantity', 0) == 0])

        self.lbl_stats.text = f"Total: {total} products  •  Active: {active}  •  Out of Stock: {out_of_stock}"

      else:
        alert(f"Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
      print(f"Error loading products: {e}")
      alert(f"Failed to load products: {str(e)}")

  def button_add_click(self, **event_args):
    """Add new product"""
    from .ProductEditForm import ProductEditForm
    result = alert(
      content=ProductEditForm(product_id=None),
      title="Add New Product",
      large=True,
      buttons=[("Cancel", False), ("Save", True)]
    )

    if result:
      self.load_products()

  def button_search_click(self, **event_args):
    """Search products"""
    self.load_products()

  def dropdown_category_filter_change(self, **event_args):
    """Filter by category"""
    self.load_products()

  def dropdown_stock_filter_change(self, **event_args):
    """Filter by stock level"""
    self.load_products()