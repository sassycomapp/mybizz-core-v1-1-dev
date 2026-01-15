from ._anvil_designer import ProductRowTemplateTemplate
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


class ProductRowTemplate(ProductRowTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    # Display image
    images = self.item.get('images', [])
    if images and len(images) > 0:
      self.img_product.source = images[0]
    else:
      self.img_product.source = "_/theme/placeholder.png"
    self.img_product.height = 50

    # Display data
    self.lbl_name.text = self.item['name']
    self.lbl_price.text = self.item['price_display']

    # Stock with color coding
    stock_text = self.item['stock_display']
    self.lbl_stock.text = stock_text

    if "Out of Stock" in stock_text:
      self.lbl_stock.foreground = "red"
    elif "(Low)" in stock_text:
      self.lbl_stock.foreground = "orange"
    else:
      self.lbl_stock.foreground = "green"

    # Status with color
    status_text = self.item['status_display']
    self.lbl_status.text = status_text

    if status_text == "Active":
      self.lbl_status.foreground = "green"
    else:
      self.lbl_status.foreground = "#999999"

    # Configure links
    self.link_edit.text = "Edit"
    self.link_edit.role = "secondary-color"

    self.link_duplicate.text = "Dupe"
    self.link_duplicate.role = "secondary-color"

    self.link_delete.text = "Del"
    self.link_delete.role = "danger"

  def link_edit_click(self, **event_args):
    """Edit product"""
    from .ProductEditForm import ProductEditForm
    result = alert(
      content=ProductEditForm(product_id=self.item.get_id()),
      title="Edit Product",
      large=True,
      buttons=[("Cancel", False), ("Save", True)]
    )

    if result:
      self.parent.parent.load_products()

  def link_duplicate_click(self, **event_args):
    """Duplicate product"""
    if confirm(f"Duplicate '{self.item['name']}'?"):
      try:
        result = anvil.server.call('duplicate_product', self.item.get_id())

        if result['success']:
          Notification("Product duplicated successfully!", style="success").show()
          self.parent.parent.load_products()
        else:
          alert(f"Error: {result.get('error', 'Unknown error')}")

      except Exception as e:
        alert(f"Failed to duplicate: {str(e)}")

  def link_delete_click(self, **event_args):
    """Delete product"""
    if confirm(f"Delete '{self.item['name']}'? This cannot be undone."):
      try:
        result = anvil.server.call('delete_product', self.item.get_id())

        if result['success']:
          Notification("Product deleted", style="success").show()
          self.parent.parent.load_products()
        else:
          alert(f"Error: {result.get('error', 'Cannot delete product with existing orders')}")

      except Exception as e:
        alert(f"Failed to delete: {str(e)}")