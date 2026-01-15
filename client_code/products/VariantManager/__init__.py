from ._anvil_designer import VariantManagerTemplate
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


class VariantManager(VariantManagerTemplate):
  """Manage product variants (size, color, style, etc.)"""

  def __init__(self, product_id=None, **properties):
    self.product_id = product_id
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "Product Variants"
    self.lbl_title.font_size = 16
    self.lbl_title.bold = True

    # Configure add button
    self.btn_add_variant.text = "Add Variant"
    self.btn_add_variant.icon = "fa:plus"
    self.btn_add_variant.role = "primary-color"

    # Configure no variants label
    self.lbl_no_variants.text = "No variants yet - click 'Add Variant' to create one."
    self.lbl_no_variants.align = "center"
    self.lbl_no_variants.foreground = "#666666"
    self.lbl_no_variants.visible = False

    # Set repeating panel template
    self.rp_variants.item_template = 'products.VariantItemTemplate'

    # Load variants
    if self.product_id:
      self.load_variants()

  def load_variants(self):
    """Load product variants"""
    try:
      result = anvil.server.call('get_product_variants', self.product_id)

      if result['success']:
        variants = result['data']

        if variants:
          self.rp_variants.items = variants
          self.rp_variants.visible = True
          self.lbl_no_variants.visible = False
        else:
          self.rp_variants.visible = False
          self.lbl_no_variants.visible = True
      else:
        alert(f"Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
      print(f"Error loading variants: {e}")
      alert(f"Failed to load variants: {str(e)}")

  def button_add_variant_click(self, **event_args):
    """Add new variant"""
    result = alert(
      content=VariantEditorModal(product_id=self.product_id, variant_id=None),
      title="Add Variant",
      large=False,
      buttons=[("Cancel", False), ("Save", True)]
    )

    if result:
      self.load_variants()

  @handle("btn_add_variant", "click")
  def btn_add_variant_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
