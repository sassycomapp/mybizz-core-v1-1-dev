from ._anvil_designer import VariantEditorModalTemplate
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


class VariantEditorModal(VariantEditorModalTemplate):
  def __init__(self, product_id=None, variant_id=None, **properties):
    self.product_id = product_id
    self.variant_id = variant_id
    self.init_components(**properties)

    # Configure fields
    self.txt_variant_name.placeholder = "e.g., Small / Red"
    self.txt_sku.placeholder = "Variant SKU (optional)"
    self.txt_price_adjustment.placeholder = "0.00"
    self.txt_price_adjustment.type = "number"
    self.txt_stock.placeholder = "0"
    self.txt_stock.type = "number"

    # Load existing variant
    if self.variant_id:
      self.load_variant()

  def load_variant(self):
    """Load existing variant"""
    try:
      result = anvil.server.call('get_variant', self.variant_id)

      if result['success']:
        variant = result['data']
        self.txt_variant_name.text = variant['variant_name']
        self.txt_sku.text = variant.get('sku', '')
        self.txt_price_adjustment.text = str(variant.get('price_adjustment', 0))
        self.txt_stock.text = str(variant.get('stock_quantity', 0))
      else:
        alert(f"Error: {result.get('error', 'Variant not found')}")

    except Exception as e:
      print(f"Error loading variant: {e}")

  def save(self):
    """Save variant"""
    if not self.txt_variant_name.text:
      alert("Variant name is required")
      return False

    try:
      variant_data = {
        'variant_name': self.txt_variant_name.text,
        'sku': self.txt_sku.text,
        'price_adjustment': float(self.txt_price_adjustment.text) if self.txt_price_adjustment.text else 0,
        'stock_quantity': int(self.txt_stock.text) if self.txt_stock.text else 0
      }

      result = anvil.server.call('save_variant', self.product_id, self.variant_id, variant_data)

      if result['success']:
        return True
      else:
        alert(f"Error: {result.get('error', 'Unknown error')}")
        return False

    except Exception as e:
      print(f"Error saving variant: {e}")
      alert(f"Failed to save: {str(e)}")
      return False