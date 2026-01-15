from ._anvil_designer import ProductDetailFormTemplate
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


class ProductDetailForm(ProductDetailFormTemplate):
  """Public product detail page"""

  def __init__(self, product_slug=None, **properties):
    self.product_slug = product_slug
    self.product = None
    self.selected_variant = None
    self.quantity = 1
    self.init_components(**properties)

    # Configure back link
    self.link_back.text = "← Back to Shop"
    self.link_back.role = "secondary-color"

    # Configure image
    self.img_main.height = 400

    # Configure quantity controls
    self.btn_decrease.text = "-"
    self.btn_decrease.role = "outlined-button"

    self.txt_quantity.text = "1"
    self.txt_quantity.type = "number"
    self.txt_quantity.width = 80

    self.btn_increase.text = "+"
    self.btn_increase.role = "outlined-button"

    # Configure action buttons
    self.btn_add_to_cart.text = "Add to Cart"
    self.btn_add_to_cart.icon = "fa:shopping-cart"
    self.btn_add_to_cart.role = "primary-color"

    self.btn_buy_now.text = "Buy Now"
    self.btn_buy_now.icon = "fa:bolt"
    self.btn_buy_now.role = "secondary-color"

    # Load product
    if self.product_slug:
      self.load_product()

  def load_product(self):
    """Load product details"""
    try:
      result = anvil.server.call('get_product_by_slug', self.product_slug)

      if result['success']:
        self.product = result['data']
        self.display_product()
      else:
        alert(f"Product not found")
        open_form('products.PublicCatalogForm')

    except Exception as e:
      print(f"Error loading product: {e}")
      alert(f"Failed to load product: {str(e)}")
      open_form('products.PublicCatalogForm')

  def display_product(self):
    """Display product information"""
    # Product name
    self.lbl_name.text = self.product['name']
    self.lbl_name.font_size = 28
    self.lbl_name.bold = True

    # Price
    price = self.product['price']
    self.lbl_price.text = f"${price:.2f}"
    self.lbl_price.font_size = 24
    self.lbl_price.foreground = "green"
    self.lbl_price.bold = True

    # Compare at price (sale)
    if self.product.get('compare_at_price') and self.product['compare_at_price'] > price:
      self.lbl_compare_price.text = f"${self.product['compare_at_price']:.2f}"
      self.lbl_compare_price.strikethrough = True
      self.lbl_compare_price.foreground = "#999999"
      self.lbl_compare_price.font_size = 18
    else:
      self.lbl_compare_price.visible = False

    # Rating (placeholder)
    self.fp_rating.clear()
    rating_label = Label(text="⭐⭐⭐⭐⭐ (12 reviews)")
    self.fp_rating.add_component(rating_label)

    # Description
    self.lbl_description.text = self.product.get('description', 'No description available.')

    # Images
    images = self.product.get('images', [])
    if images:
      self.img_main.source = images[0]

      # Thumbnails
      self.fp_thumbnails.clear()
      for img in images:
        thumb = Image(
          source=img,
          height=80,
          spacing_above='small',
          spacing_below='small'
        )
        thumb.tag = img
        thumb.set_event_handler('click', self.thumbnail_click)
        self.fp_thumbnails.add_component(thumb)
    else:
      self.img_main.source = "_/theme/placeholder.png"

    # Load variants
    self.load_variants()

    # Stock status
    self.update_stock_status()

    # Share buttons (placeholder)
    self.fp_share.clear()
    share_label = Label(text="Share: 📘 🐦 📧")
    self.fp_share.add_component(share_label)

  def load_variants(self):
    """Load product variants"""
    try:
      result = anvil.server.call('get_product_variants', self.product.get_id())

      if result['success'] and result['data']:
        variants = result['data']

        # Show variant dropdown
        items = [('Select Variant', None)]
        for v in variants:
          items.append((v['variant_name'], v.get_id()))

        self.dd_variant.items = items
        self.dd_variant.visible = True
      else:
        # No variants
        self.dd_variant.visible = False

    except Exception as e:
      print(f"Error loading variants: {e}")
      self.dd_variant.visible = False

  def update_stock_status(self):
    """Update stock availability display"""
    stock = self.product.get('inventory_quantity', 0)

    if stock > 10:
      self.lbl_stock_status.text = f"✅ In Stock ({stock} available)"
      self.lbl_stock_status.foreground = "green"
      self.btn_add_to_cart.enabled = True
      self.btn_buy_now.enabled = True
    elif stock > 0:
      self.lbl_stock_status.text = f"⚠️ Low Stock (only {stock} left)"
      self.lbl_stock_status.foreground = "orange"
      self.btn_add_to_cart.enabled = True
      self.btn_buy_now.enabled = True
    else:
      self.lbl_stock_status.text = "❌ Out of Stock"
      self.lbl_stock_status.foreground = "red"
      self.btn_add_to_cart.enabled = False
      self.btn_buy_now.enabled = False

  def thumbnail_click(self, sender, **event_args):
    """Change main image"""
    self.img_main.source = sender.tag

  def button_decrease_click(self, **event_args):
    """Decrease quantity"""
    try:
      current = int(self.txt_quantity.text)
      if current > 1:
        self.txt_quantity.text = str(current - 1)
    except:
      self.txt_quantity.text = "1"

  def button_increase_click(self, **event_args):
    """Increase quantity"""
    try:
      current = int(self.txt_quantity.text)
      stock = self.product.get('inventory_quantity', 0)

      if current < stock:
        self.txt_quantity.text = str(current + 1)
      else:
        alert(f"Only {stock} available")
    except:
      self.txt_quantity.text = "1"

  def button_add_to_cart_click(self, **event_args):
    """Add to cart"""
    try:
      quantity = int(self.txt_quantity.text)

      if quantity < 1:
        alert("Quantity must be at least 1")
        return

      # Get variant if selected
      variant_id = self.dd_variant.selected_value if self.dd_variant.visible else None

      result = anvil.server.call('add_to_cart', self.product.get_id(), variant_id, quantity)

      if result['success']:
        Notification("Added to cart!", style="success").show()
      else:
        alert(f"Error: {result.get('error', 'Could not add to cart')}")

    except ValueError:
      alert("Please enter a valid quantity")
    except Exception as e:
      print(f"Error adding to cart: {e}")
      alert(f"Failed to add to cart: {str(e)}")

  def button_buy_now_click(self, **event_args):
    """Buy now - add to cart and go to checkout"""
    try:
      quantity = int(self.txt_quantity.text)
      variant_id = self.dd_variant.selected_value if self.dd_variant.visible else None

      result = anvil.server.call('add_to_cart', self.product.get_id(), variant_id, quantity)

      if result['success']:
        # Go directly to cart/checkout
        open_form('products.CartForm')
      else:
        alert(f"Error: {result.get('error', 'Could not add to cart')}")

    except ValueError:
      alert("Please enter a valid quantity")
    except Exception as e:
      print(f"Error: {e}")
      alert(f"Failed: {str(e)}")

  def link_back_click(self, **event_args):
    """Go back to catalog"""
    open_form('products.PublicCatalogForm')