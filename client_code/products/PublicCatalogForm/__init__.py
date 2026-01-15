from ._anvil_designer import PublicCatalogFormTemplate
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


class PublicCatalogForm(PublicCatalogFormTemplate):
  """Public product catalog - customer shopping"""

  def __init__(self, **properties):
    self.current_category = None
    self.current_page = 1
    self.products_per_page = 20
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "Shop"
    self.lbl_title.font_size = 24
    self.lbl_title.bold = True

    # Configure cart button
    self.update_cart_button()

    # Configure search
    self.txt_search.placeholder = "Search products..."
    self.txt_search.icon = "fa:search"

    self.btn_search.text = ""
    self.btn_search.icon = "fa:search"
    self.btn_search.role = "secondary-color"

    # Configure sort
    self.dd_sort.items = [
      ('Newest', 'newest'),
      ('Price: Low to High', 'price_asc'),
      ('Price: High to Low', 'price_desc'),
      ('Name: A-Z', 'name_asc')
    ]
    self.dd_sort.selected_value = 'newest'

    # Set repeating panel template
    self.rp_products.item_template = 'products.ProductCardTemplate'

    # Load categories
    self.load_categories()

    # Load products
    self.load_products()

  def load_categories(self):
    """Load category sidebar"""
    try:
      categories = anvil.server.call('get_public_categories')

      # Add "All Products" option
      all_link = Link(
        text="All Products",
        font_size=14,
        bold=True,
        spacing_above='small',
        spacing_below='small'
      )
      all_link.tag = None
      all_link.set_event_handler('click', self.category_link_click)
      self.col_sidebar.add_component(all_link)

      # Add separator
      self.col_sidebar.add_component(Label(text="───", foreground="#CCCCCC"))

      # Add category links
      for cat in categories:
        link = Link(
          text=cat['name'],
          font_size=14,
          spacing_above='small',
          spacing_below='small'
        )
        link.tag = cat.get_id()
        link.set_event_handler('click', self.category_link_click)
        self.col_sidebar.add_component(link)

    except Exception as e:
      print(f"Error loading categories: {e}")

  def load_products(self):
    """Load products with filters and pagination"""
    try:
      filters = {
        'search': self.txt_search.text,
        'category_id': self.current_category,
        'sort': self.dd_sort.selected_value,
        'page': self.current_page,
        'per_page': self.products_per_page
      }

      result = anvil.server.call('get_public_products', filters)

      if result['success']:
        products = result['data']['products']
        total_count = result['data']['total_count']

        self.rp_products.items = products

        # Update pagination
        self.update_pagination(total_count)

      else:
        alert(f"Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
      print(f"Error loading products: {e}")
      alert(f"Failed to load products: {str(e)}")

  def update_pagination(self, total_count):
    """Update pagination controls"""
    self.col_pagination.clear()

    total_pages = (total_count + self.products_per_page - 1) // self.products_per_page

    if total_pages <= 1:
      return

    pagination_panel = FlowPanel(spacing='small')

    # Previous button
    if self.current_page > 1:
      btn_prev = Button(text="< Prev", role="outlined-button")
      btn_prev.set_event_handler('click', self.prev_page_click)
      pagination_panel.add_component(btn_prev)

    # Page info
    page_label = Label(text=f"Page {self.current_page} of {total_pages}")
    pagination_panel.add_component(page_label)

    # Next button
    if self.current_page < total_pages:
      btn_next = Button(text="Next >", role="outlined-button")
      btn_next.set_event_handler('click', self.next_page_click)
      pagination_panel.add_component(btn_next)

    self.col_pagination.add_component(pagination_panel)

  def update_cart_button(self):
    """Update cart button with item count"""
    try:
      result = anvil.server.call('get_cart_count')
      count = result.get('count', 0)

      if count > 0:
        self.btn_cart.text = f"🛒 Cart ({count})"
        self.btn_cart.role = "primary-color"
      else:
        self.btn_cart.text = "🛒 Cart"
        self.btn_cart.role = "outlined-button"

    except Exception as e:
      print(f"Error updating cart: {e}")
      self.btn_cart.text = "🛒 Cart"

  def category_link_click(self, sender, **event_args):
    """Filter by category"""
    self.current_category = sender.tag
    self.current_page = 1
    self.load_products()

  def button_search_click(self, **event_args):
    """Search products"""
    self.current_page = 1
    self.load_products()

  def dropdown_sort_change(self, **event_args):
    """Sort products"""
    self.current_page = 1
    self.load_products()

  def prev_page_click(self, sender, **event_args):
    """Go to previous page"""
    if self.current_page > 1:
      self.current_page -= 1
      self.load_products()

  def next_page_click(self, sender, **event_args):
    """Go to next page"""
    self.current_page += 1
    self.load_products()

  def button_cart_click(self, **event_args):
    """View cart"""
    open_form('products.CartForm')

  @handle("btn_cart", "click")
  def btn_cart_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_search", "click")
  def btn_search_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("dd_sort", "change")
  def dd_sort_change(self, **event_args):
    """This method is called when an item is selected"""
    pass
