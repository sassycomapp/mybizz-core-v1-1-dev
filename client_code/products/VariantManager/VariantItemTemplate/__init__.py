from ._anvil_designer import VariantItemTemplateTemplate
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


class VariantItemTemplate(VariantItemTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    # Display data
    self.lbl_name.text = self.item['variant_name']
    self.lbl_name.bold = True

    self.lbl_sku.text = self.item.get('sku', 'N/A')

    # Price adjustment
    price_adj = self.item.get('price_adjustment', 0)
    if price_adj >= 0:
      self.lbl_price_adj.text = f"+${price_adj:.2f}"
    else:
      self.lbl_price_adj.text = f"-${abs(price_adj):.2f}"

    self.lbl_stock.text = str(self.item.get('stock_quantity', 0))

    # Links
    self.link_edit.text = "Edit"
    self.link_edit.role = "secondary-color"

    self.link_delete.text = "Delete"
    self.link_delete.role = "danger"

  def link_edit_click(self, **event_args):
    """Edit variant"""
    result = alert(
      content=VariantEditorModal(
        product_id=self.item['product_id'].get_id(),
        variant_id=self.item.get_id()
      ),
      title="Edit Variant",
      large=False,
      buttons=[("Cancel", False), ("Save", True)]
    )

    if result:
      self.parent.parent.load_variants()

  def link_delete_click(self, **event_args):
    """Delete variant"""
    if confirm(f"Delete variant '{self.item['variant_name']}'?"):
      try:
        result = anvil.server.call('delete_variant', self.item.get_id())

        if result['success']:
          Notification("Variant deleted", style="success").show()
          self.parent.parent.load_variants()
        else:
          alert(f"Error: {result.get('error', 'Unknown error')}")

      except Exception as e:
        alert(f"Failed to delete: {str(e)}")