from ._anvil_designer import ProductEditFormTemplate
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


class ProductEditForm(ProductEditFormTemplate):
  """Product create/edit form"""

  def __init__(self, product_id=None, **properties):
    self.product_id = product_id
    self.product = None
    self.uploaded_images = []
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "Edit Product" if product_id else "Add New Product"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True

    # Configure back link
    self.link_back.text = "← Back to Products"
    self.link_back.role = "secondary-color"

    # Configure fields
    self.txt_name.placeholder = "Product name"
    self.txt_slug.placeholder = "url-friendly-name (auto-generated)"

    self.txt_description.placeholder = "Full product description..."
    self.txt_description.rows = 8

    self.txt_price.placeholder = "0.00"
    self.txt_price.type = "number"

    self.txt_compare_price.placeholder = "0.00 (optional)"
    self.txt_compare_price.type = "number"

    self.txt_cost.placeholder = "0.00 (optional)"
    self.txt_cost.type = "number"

    # Product type
    self.lbl_product_type.text = "Product Type:"
    self.lbl_product_type.bold = True

    self.rb_physical.text = "Physical"
    self.rb_physical.group_name = "product_type"
    self.rb_physical.selected = True

    self.rb_digital.text = "Digital"
    self.rb_digital.group_name = "product_type"

    self.rb_service.text = "Service"
    self.rb_service.group_name = "product_type"

    # Physical product fields
    self.txt_sku.placeholder = "SKU/Product Code"
    self.txt_stock.placeholder = "0"
    self.txt_stock.type = "number"

    self.txt_low_stock_alert.placeholder = "10"
    self.txt_low_stock_alert.type = "number"

    self.txt_weight.placeholder = "0.0"
    self.txt_weight.type = "number"

    self.cb_track_inventory.text = "Track inventory"
    self.cb_track_inventory.checked = True

    self.cb_allow_backorders.text = "Allow backorders (sell when out of stock)"
    self.cb_allow_backorders.checked = False

    # Active checkbox
    self.cb_active.text = "Active (visible to customers)"
    self.cb_active.checked = True

    # Buttons
    self.btn_cancel.text = "Cancel"
    self.btn_cancel.role = "outlined-button"

    self.btn_save.text = "Save"
    self.btn_save.role = "primary-color"

    self.btn_save_and_new.text = "Save & Add Another"
    self.btn_save_and_new.role = "outlined-button"

    # Load categories
    self.load_categories()

    # Load product if editing
    if self.product_id:
      self.load_product()

    # Initially show physical fields
    self.toggle_product_type_fields()

  def load_categories(self):
    """Load product categories"""
    try:
      categories = anvil.server.call('get_all_categories')

      items = [('Select Category', None)]
      for cat in categories:
        items.append((cat['name'], cat.get_id()))

      self.dd_category.items = items

    except Exception as e:
      print(f"Error loading categories: {e}")

  def load_product(self):
    """Load existing product"""
    try:
      result = anvil.server.call('get_product', self.product_id)

      if result['success']:
        self.product = result['data']

        # Populate fields
        self.txt_name.text = self.product['name']
        self.txt_slug.text = self.product['slug']

        if self.product.get('category_id'):
          self.dd_category.selected_value = self.product['category_id'].get_id()

        self.txt_description.text = self.product.get('description', '')
        self.txt_price.text = str(self.product['price'])

        if self.product.get('compare_at_price'):
          self.txt_compare_price.text = str(self.product['compare_at_price'])

        if self.product.get('cost'):
          self.txt_cost.text = str(self.product['cost'])

        # Physical fields
        self.txt_sku.text = self.product.get('sku', '')
        self.txt_stock.text = str(self.product.get('inventory_quantity', 0))
        self.txt_weight.text = str(self.product.get('weight', ''))

        self.cb_track_inventory.checked = self.product.get('track_inventory', True)
        self.cb_allow_backorders.checked = self.product.get('allow_backorders', False)

        # Active status
        self.cb_active.checked = self.product.get('is_active', True)

        # Show existing images
        images = self.product.get('images', [])
        for img_url in images:
          self.add_image_preview(img_url)

      else:
        alert(f"Error: {result.get('error', 'Product not found')}")

    except Exception as e:
      print(f"Error loading product: {e}")
      alert(f"Failed to load product: {str(e)}")

  def toggle_product_type_fields(self):
    """Show/hide fields based on product type"""
    # For now, always show physical fields
    # In future, add digital/service specific fields
    is_physical = self.rb_physical.selected
    self.col_physical_fields.visible = is_physical

  def text_name_change(self, **event_args):
    """Auto-generate slug from name"""
    if not self.product_id:  # Only auto-generate for new products
      name = self.txt_name.text or ""
      slug = self.generate_slug(name)
      self.txt_slug.text = slug

  def generate_slug(self, text):
    """Generate URL-friendly slug"""
    # Convert to lowercase
    slug = text.lower()
    # Replace spaces with hyphens
    slug = slug.replace(' ', '-')
    # Remove special characters
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    # Remove multiple hyphens
    slug = re.sub(r'-+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    return slug

  @handle("file_images", "change")
  def file_images_change(self, file, **event_args):
    """Handle image upload"""
    if file:
      self.uploaded_images.append(file)
      self.add_image_preview(file)

  def add_image_preview(self, image):
    """Add image preview to flow panel"""
    img = Image(
      source=image,
      height=100,
      spacing_above='small',
      spacing_below='small'
    )
    self.fp_image_preview.add_component(img)

  def validate_form(self):
    """Validate form inputs"""
    if not self.txt_name.text:
      alert("Product name is required")
      return False

    if not self.txt_slug.text:
      alert("Slug is required")
      return False

    if not self.txt_price.text or float(self.txt_price.text) <= 0:
      alert("Valid price is required")
      return False

    return True

  def save_product(self, add_another=False):
    """Save product"""
    if not self.validate_form():
      return False

    try:
      product_data = {
        'name': self.txt_name.text,
        'slug': self.txt_slug.text,
        'category_id': self.dd_category.selected_value,
        'description': self.txt_description.text,
        'price': float(self.txt_price.text),
        'compare_at_price': float(self.txt_compare_price.text) if self.txt_compare_price.text else None,
        'cost': float(self.txt_cost.text) if self.txt_cost.text else None,
        'sku': self.txt_sku.text,
        'inventory_quantity': int(self.txt_stock.text) if self.txt_stock.text else 0,
        'weight': float(self.txt_weight.text) if self.txt_weight.text else None,
        'track_inventory': self.cb_track_inventory.checked,
        'allow_backorders': self.cb_allow_backorders.checked,
        'is_active': self.cb_active.checked,
        'uploaded_images': self.uploaded_images
      }

      result = anvil.server.call('save_product', self.product_id, product_data)

      if result['success']:
        Notification("Product saved successfully!", style="success").show()

        if add_another:
          # Reset form for new product
          self.product_id = None
          self.reset_form()

        return True
      else:
        alert(f"Error: {result.get('error', 'Unknown error')}")
        return False

    except Exception as e:
      print(f"Error saving product: {e}")
      alert(f"Failed to save: {str(e)}")
      return False

  def reset_form(self):
    """Reset form for new entry"""
    self.txt_name.text = ""
    self.txt_slug.text = ""
    self.dd_category.selected_value = None
    self.txt_description.text = ""
    self.txt_price.text = ""
    self.txt_compare_price.text = ""
    self.txt_cost.text = ""
    self.txt_sku.text = ""
    self.txt_stock.text = ""
    self.txt_weight.text = ""
    self.uploaded_images = []
    self.fp_image_preview.clear()
    self.cb_active.checked = True

  def button_save_click(self, **event_args):
    """Save and close"""
    if self.save_product():
      self.raise_event('x-close-alert', value=True)

  def button_save_and_new_click(self, **event_args):
    """Save and add another"""
    self.save_product(add_another=True)

  def button_cancel_click(self, **event_args):
    """Cancel editing"""
    self.raise_event('x-close-alert', value=False)

  @handle("link_back", "click")
  def link_back_click(self, **event_args):
    """Go back to product list"""
    open_form('products.ProductListForm')

  def radio_button_clicked(self, **event_args):
    """Product type changed"""
    self.toggle_product_type_fields()

  @handle("txt_name", "pressed_enter")
  def txt_name_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    pass

  @handle("rb_physical", "clicked")
  def rb_physical_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    pass

  @handle("rb_digital", "clicked")
  def rb_digital_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    pass

  @handle("rb_service", "clicked")
  def rb_service_clicked(self, **event_args):
    """This method is called when this radio button is selected"""
    pass

  @handle("btn_cancel", "click")
  def btn_cancel_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_save", "click")
  def btn_save_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_save_and_new", "click")
  def btn_save_and_new_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
