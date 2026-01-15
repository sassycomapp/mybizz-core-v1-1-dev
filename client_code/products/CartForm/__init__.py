from ._anvil_designer import CartFormTemplate
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


class CartForm(CartFormTemplate):
  """Shopping cart view"""

  def __init__(self, **properties):
    self.cart_items = []
    self.init_components(**properties)

    # Configure title
    self.lbl_title.font_size = 24
    self.lbl_title.bold = True

    # Configure continue shopping button
    self.btn_continue_shopping.text = "Continue Shopping"
    self.btn_continue_shopping.icon = "fa:arrow-left"
    self.btn_continue_shopping.role = "outlined-button"

    # Configure empty state
    self.lbl_empty.text = "Your cart is empty"
    self.lbl_empty.font_size = 20
    self.lbl_empty.align = "center"
    self.lbl_empty.foreground = "#666666"

    self.btn_shop_empty.text = "Continue Shopping"
    self.btn_shop_empty.role = "primary-color"

    # Configure checkout button
    self.btn_checkout.text = "Proceed to Checkout"
    self.btn_checkout.icon = "fa:arrow-right"
    self.btn_checkout.role = "primary-color"

    # Set repeating panel template
    self.rp_cart_items.item_template = 'products.CartItemTemplate'

    # Load cart
    self.load_cart()

  def load_cart(self):
    """Load cart items"""
    try:
      result = anvil.server.call('get_cart')

      if result['success']:
        self.cart_items = result['data']

        if self.cart_items:
          # Show cart items
          self.lbl_title.text = f"Shopping Cart ({len(self.cart_items)} items)"
          self.rp_cart_items.items = self.cart_items
          self.rp_cart_items.visible = True
          self.col_empty.visible = False
          self.col_summary.visible = True

          # Calculate totals
          self.calculate_totals()
        else:
          # Show empty state
          self.lbl_title.text = "Shopping Cart"
          self.rp_cart_items.visible = False
          self.col_empty.visible = True
          self.col_summary.visible = False

      else:
        alert(f"Error: {result.get('error', 'Could not load cart')}")

    except Exception as e:
      print(f"Error loading cart: {e}")
      alert(f"Failed to load cart: {str(e)}")

  def calculate_totals(self):
    """Calculate and display totals"""
    subtotal = sum(item['subtotal'] for item in self.cart_items)

    # TODO: Get tax rate from config
    tax_rate = 0.10  # 10%
    tax = subtotal * tax_rate

    total = subtotal + tax

    self.lbl_subtotal.text = f"Subtotal: ${subtotal:.2f}"
    self.lbl_subtotal.font_size = 16

    self.lbl_tax.text = f"Tax ({tax_rate*100:.0f}%): ${tax:.2f}"
    self.lbl_tax.font_size = 16

    self.lbl_total.text = f"Total: ${total:.2f}"
    self.lbl_total.font_size = 20
    self.lbl_total.bold = True

  def button_continue_shopping_click(self, **event_args):
    """Go back to catalog"""
    open_form('products.PublicCatalogForm')

  def button_shop_empty_click(self, **event_args):
    """Go to catalog from empty state"""
    open_form('products.PublicCatalogForm')

  def button_checkout_click(self, **event_args):
    """Proceed to checkout"""
    if not self.cart_items:
      alert("Your cart is empty")
      return

    open_form('products.CheckoutForm')

  @handle("btn_continue_shopping", "click")
  def btn_continue_shopping_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_shop_empty", "click")
  def btn_shop_empty_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_checkout", "click")
  def btn_checkout_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
