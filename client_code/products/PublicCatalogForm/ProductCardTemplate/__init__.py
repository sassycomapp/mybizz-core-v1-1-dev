from ._anvil_designer import ProductCardTemplateTemplate
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


class ProductCardTemplate(ProductCardTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    # Display image
    images = self.item.get('images', [])
    if images and len(images) > 0:
      self.img_product.source = images[0]
    else:
      self.img_product.source = "_/theme/placeholder.png"
    self.img_product.height = 200

    # Make image clickable
    self.img_product.role = "clickable"
    self.img_product.set_event_handler('click', self.image_click)

    # Display name
    self.lbl_name.text = self.item['name']
    self.lbl_name.bold = True
    self.lbl_name.font_size = 14

    # Display price
    self.lbl_price.text = f"${self.item['price']:.2f}"
    self.lbl_price.font_size = 16
    self.lbl_price.foreground = "green"

    # Add to cart button
    self.btn_add_to_cart.text = "Add to Cart"
    self.btn_add_to_cart.icon = "fa:plus"
    self.btn_add_to_cart.role = "primary-color"

    # Check stock
    stock = self.item.get('inventory_quantity', 0)
    if stock == 0:
      self.btn_add_to_cart.text = "Out of Stock"
      self.btn_add_to_cart.enabled = False

  def image_click(self, **event_args):
    """View product details"""
    open_form('products.ProductDetailForm', product_slug=self.item['slug'])

  def button_add_to_cart_click(self, **event_args):
    """Add product to cart"""
    try:
      result = anvil.server.call('add_to_cart', self.item.get_id(), None, 1)

      if result['success']:
        Notification("Added to cart!", style="success").show()
        # Update parent's cart button
        self.parent.parent.update_cart_button()
      else:
        alert(f"Error: {result.get('error', 'Could not add to cart')}")

    except Exception as e:
      print(f"Error adding to cart: {e}")
      alert(f"Failed to add to cart: {str(e)}")

  @handle("btn_add_to_cart", "click")
  def btn_add_to_cart_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
