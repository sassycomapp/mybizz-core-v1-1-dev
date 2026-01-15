from ._anvil_designer import CartItemTemplateTemplate
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


class CartItemTemplate(CartItemTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    # Display image
    product_images = self.item['product_id'].get('images', [])
    if product_images:
      self.img_product.source = product_images[0]
    else:
      self.img_product.source = "_/theme/placeholder.png"
    self.img_product.height = 80

    # Display product name
    self.lbl_name.text = self.item['product_id']['name']
    self.lbl_name.bold = True
    self.lbl_name.font_size = 16

    # Display variant if exists
    if self.item.get('variant_id'):
      self.lbl_variant.text = f"({self.item['variant_id']['variant_name']})"
      self.lbl_variant.foreground = "#666666"
    else:
      self.lbl_variant.visible = False

    # Display price
    self.lbl_price.text = f"${self.item['price_at_add']:.2f}"

    # Quantity controls
    self.btn_decrease.text = "-"
    self.btn_decrease.role = "outlined-button"

    self.txt_quantity.text = str(self.item['quantity'])
    self.txt_quantity.type = "number"
    self.txt_quantity.width = 60

    self.btn_increase.text = "+"
    self.btn_increase.role = "outlined-button"

    # Subtotal
    subtotal = self.item['price_at_add'] * self.item['quantity']
    self.lbl_subtotal.text = f"${subtotal:.2f}"
    self.lbl_subtotal.bold = True

    # Remove link
    self.link_remove.text = "Remove"
    self.link_remove.role = "danger"

  def button_decrease_click(self, **event_args):
    """Decrease quantity"""
    try:
      current = int(self.txt_quantity.text)
      if current > 1:
        new_qty = current - 1
        self.update_quantity(new_qty)
    except:
      pass

  def button_increase_click(self, **event_args):
    """Increase quantity"""
    try:
      current = int(self.txt_quantity.text)
      # Check stock
      stock = self.item['product_id'].get('inventory_quantity', 0)

      if current < stock:
        new_qty = current + 1
        self.update_quantity(new_qty)
      else:
        alert(f"Only {stock} available")
    except:
      pass

  def update_quantity(self, new_qty):
    """Update item quantity"""
    try:
      result = anvil.server.call('update_cart_quantity', self.item.get_id(), new_qty)

      if result['success']:
        self.txt_quantity.text = str(new_qty)
        # Refresh parent cart
        self.parent.parent.load_cart()
      else:
        alert(f"Error: {result.get('error', 'Could not update')}")

    except Exception as e:
      print(f"Error updating quantity: {e}")
      alert(f"Failed to update: {str(e)}")

  @handle("link_remove", "click")
  def link_remove_click(self, **event_args):
    """Remove item from cart"""
    if confirm("Remove this item from cart?"):
      try:
        result = anvil.server.call('remove_cart_item', self.item.get_id())

        if result['success']:
          Notification("Item removed", style="success").show()
          self.parent.parent.load_cart()
        else:
          alert(f"Error: {result.get('error', 'Could not remove')}")

      except Exception as e:
        print(f"Error removing item: {e}")
        alert(f"Failed to remove: {str(e)}")

  @handle("btn_decrease", "click")
  def btn_decrease_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_increase", "click")
  def btn_increase_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("txt_quantity", "pressed_enter")
  def txt_quantity_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    pass
