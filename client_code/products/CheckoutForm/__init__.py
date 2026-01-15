from ._anvil_designer import CheckoutFormTemplate
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


class CheckoutForm(CheckoutFormTemplate):
  """Multi-step checkout process"""

  def __init__(self, **properties):
    self.current_step = 1
    self.total_steps = 4
    self.cart_items = []
    self.customer_data = {}
    self.shipping_data = {}
    self.payment_method = None
    self.init_components(**properties)

    # Check authentication
    user = anvil.users.get_user()
    if not user:
      if not confirm("You need to login to checkout. Login now?"):
        open_form('products.CartForm')
        return
      else:
        open_form('auth.LoginForm')
        return

    # Configure title
    self.lbl_title.text = "Checkout"
    self.lbl_title.font_size = 24
    self.lbl_title.bold = True

    # Configure buttons
    self.btn_back.text = "← Back"
    self.btn_back.role = "outlined-button"

    self.btn_next.text = "Continue →"
    self.btn_next.role = "primary-color"

    # Load cart
    self.load_cart()

    # Show first step
    self.show_step(1)

  def load_cart(self):
    """Load cart items for checkout"""
    try:
      result = anvil.server.call('get_cart')

      if result['success']:
        self.cart_items = result['data']

        if not self.cart_items:
          alert("Your cart is empty")
          open_form('products.CartForm')
      else:
        alert(f"Error loading cart: {result.get('error')}")
        open_form('products.CartForm')

    except Exception as e:
      print(f"Error loading cart: {e}")
      alert("Failed to load cart")
      open_form('products.CartForm')

  def show_step(self, step):
    """Display the current checkout step"""
    self.current_step = step

    # Update step indicator
    self.lbl_step_indicator.text = f"Step {step} of {self.total_steps}"

    # Update step circles
    self.update_step_indicator()

    # Clear current content
    self.col_step_content.clear()

    # Show appropriate step
    if step == 1:
      self.show_contact_info()
      self.btn_back.text = "← Back to Cart"
      self.btn_next.text = "Continue to Shipping →"
    elif step == 2:
      self.show_shipping_address()
      self.btn_back.text = "← Back"
      self.btn_next.text = "Continue to Payment →"
    elif step == 3:
      self.show_payment_method()
      self.btn_back.text = "← Back"
      self.btn_next.text = "Continue to Review →"
    elif step == 4:
      self.show_order_review()
      self.btn_back.text = "← Back"
      self.btn_next.text = "Place Order"

  def update_step_indicator(self):
    """Update visual step indicator"""
    self.fp_steps.clear()

    step_names = ["Contact", "Shipping", "Payment", "Review"]

    for i, name in enumerate(step_names, 1):
      if i < self.current_step:
        icon = "● "  # Completed
        color = "green"
      elif i == self.current_step:
        icon = "● "  # Current
        color = "#2196F3"
      else:
        icon = "○ "  # Pending
        color = "#CCCCCC"

      label = Label(
        text=f"{icon}{name}",
        foreground=color,
        spacing_above='small',
        spacing_below='small'
      )
      self.fp_steps.add_component(label)

  def show_contact_info(self):
    """Step 1: Contact Information"""
    title = Label(text="Contact Information", font_size=18, bold=True)
    self.col_step_content.add_component(title)

    # Pre-fill with user data if available
    user = anvil.users.get_user()

    self.txt_email = TextBox(
      placeholder="Email",
      text=user['email'] if user else "",
      spacing_above='medium'
    )
    self.col_step_content.add_component(self.txt_email)

    self.txt_first_name = TextBox(
      placeholder="First Name",
      text=self.customer_data.get('first_name', ''),
      spacing_above='small'
    )
    self.col_step_content.add_component(self.txt_first_name)

    self.txt_last_name = TextBox(
      placeholder="Last Name",
      text=self.customer_data.get('last_name', ''),
      spacing_above='small'
    )
    self.col_step_content.add_component(self.txt_last_name)

    self.txt_phone = TextBox(
      placeholder="Phone Number",
      text=self.customer_data.get('phone', ''),
      spacing_above='small'
    )
    self.col_step_content.add_component(self.txt_phone)

  def show_shipping_address(self):
    """Step 2: Shipping Address"""
    title = Label(text="Shipping Address", font_size=18, bold=True)
    self.col_step_content.add_component(title)

    self.txt_address1 = TextBox(
      placeholder="Address Line 1",
      text=self.shipping_data.get('address1', ''),
      spacing_above='medium'
    )
    self.col_step_content.add_component(self.txt_address1)

    self.txt_address2 = TextBox(
      placeholder="Address Line 2 (optional)",
      text=self.shipping_data.get('address2', ''),
      spacing_above='small'
    )
    self.col_step_content.add_component(self.txt_address2)

    self.txt_city = TextBox(
      placeholder="City",
      text=self.shipping_data.get('city', ''),
      spacing_above='small'
    )
    self.col_step_content.add_component(self.txt_city)

    row = FlowPanel(spacing='small', spacing_above='small')

    self.txt_state = TextBox(
      placeholder="State",
      text=self.shipping_data.get('state', ''),
      width=150
    )
    row.add_component(self.txt_state)

    self.txt_zip = TextBox(
      placeholder="ZIP",
      text=self.shipping_data.get('zip', ''),
      width=150
    )
    row.add_component(self.txt_zip)

    self.col_step_content.add_component(row)

    self.dd_country = DropDown(
      items=[('United States', 'US'), ('Canada', 'CA'), ('United Kingdom', 'UK')],
      selected_value=self.shipping_data.get('country', 'US'),
      spacing_above='small'
    )
    self.col_step_content.add_component(self.dd_country)

  def show_payment_method(self):
    """Step 3: Payment Method"""
    title = Label(text="Payment Method", font_size=18, bold=True)
    self.col_step_content.add_component(title)

    self.rb_stripe = RadioButton(
      text="Credit Card (Stripe)",
      group_name="payment",
      selected=True,
      spacing_above='medium'
    )
    self.col_step_content.add_component(self.rb_stripe)

    self.rb_paystack = RadioButton(
      text="Mobile Money (Paystack)",
      group_name="payment",
      spacing_above='small'
    )
    self.col_step_content.add_component(self.rb_paystack)

    # Payment form placeholder
    info = Label(
      text="Payment will be processed securely through your selected gateway.",
      foreground="#666666",
      italic=True,
      spacing_above='medium'
    )
    self.col_step_content.add_component(info)

  def show_order_review(self):
    """Step 4: Order Review"""
    title = Label(text="Order Review", font_size=18, bold=True)
    self.col_step_content.add_component(title)

    # Contact info
    contact = Label(
      text=f"Contact: {self.customer_data['email']}",
      spacing_above='medium'
    )
    self.col_step_content.add_component(contact)

    # Shipping address
    shipping = Label(
      text=f"Ship to: {self.shipping_data['address1']}, {self.shipping_data['city']}, {self.shipping_data['state']} {self.shipping_data['zip']}",
      spacing_above='small'
    )
    self.col_step_content.add_component(shipping)

    # Items
    items_title = Label(
      text=f"Items ({len(self.cart_items)}):",
      bold=True,
      spacing_above='medium'
    )
    self.col_step_content.add_component(items_title)

    for item in self.cart_items:
      product_name = item['product_id']['name']
      variant = f" ({item['variant_id']['variant_name']})" if item.get('variant_id') else ""
      qty = item['quantity']
      subtotal = item['subtotal']

      item_label = Label(
        text=f"• {product_name}{variant} x {qty} - ${subtotal:.2f}",
        spacing_above='small'
      )
      self.col_step_content.add_component(item_label)

    # Totals
    subtotal = sum(item['subtotal'] for item in self.cart_items)
    tax = subtotal * 0.10
    shipping_cost = 5.00  # Fixed for now
    total = subtotal + tax + shipping_cost

    self.col_step_content.add_component(Label(text="", spacing_above='medium'))

    subtotal_label = Label(text=f"Subtotal: ${subtotal:.2f}")
    self.col_step_content.add_component(subtotal_label)

    tax_label = Label(text=f"Tax: ${tax:.2f}", spacing_above='small')
    self.col_step_content.add_component(tax_label)

    shipping_label = Label(text=f"Shipping: ${shipping_cost:.2f}", spacing_above='small')
    self.col_step_content.add_component(shipping_label)

    total_label = Label(
      text=f"Total: ${total:.2f}",
      font_size=18,
      bold=True,
      spacing_above='small'
    )
    self.col_step_content.add_component(total_label)

  def validate_current_step(self):
    """Validate current step before proceeding"""
    if self.current_step == 1:
      # Validate contact info
      if not self.txt_email.text or '@' not in self.txt_email.text:
        alert("Please enter a valid email")
        return False
      if not self.txt_first_name.text or not self.txt_last_name.text:
        alert("Please enter your name")
        return False

      # Save data
      self.customer_data = {
        'email': self.txt_email.text,
        'first_name': self.txt_first_name.text,
        'last_name': self.txt_last_name.text,
        'phone': self.txt_phone.text
      }
      return True

    elif self.current_step == 2:
      # Validate shipping
      if not self.txt_address1.text:
        alert("Please enter your address")
        return False
      if not self.txt_city.text or not self.txt_state.text or not self.txt_zip.text:
        alert("Please complete your address")
        return False

      # Save data
      self.shipping_data = {
        'address1': self.txt_address1.text,
        'address2': self.txt_address2.text,
        'city': self.txt_city.text,
        'state': self.txt_state.text,
        'zip': self.txt_zip.text,
        'country': self.dd_country.selected_value
      }
      return True

    elif self.current_step == 3:
      # Validate payment
      if self.rb_stripe.selected:
        self.payment_method = 'stripe'
      elif self.rb_paystack.selected:
        self.payment_method = 'paystack'
      else:
        alert("Please select a payment method")
        return False
      return True

    return True

  def button_next_click(self, **event_args):
    """Next/Submit button"""
    if self.current_step == 4:
      # Place order
      self.place_order()
    else:
      # Validate and go to next step
      if self.validate_current_step():
        self.show_step(self.current_step + 1)

  def button_back_click(self, **event_args):
    """Back button"""
    if self.current_step == 1:
      # Go back to cart
      open_form('products.CartForm')
    else:
      # Go to previous step
      self.show_step(self.current_step - 1)

  def place_order(self):
    """Process the order"""
    try:
      # Show loading
      with Notification("Processing order..."):
        result = anvil.server.call(
          'create_order_from_cart',
          self.customer_data,
          self.shipping_data,
          self.payment_method
        )

      if result['success']:
        order_number = result['order_number']
        Notification(f"Order {order_number} placed successfully!", style="success").show()

        # Redirect to order confirmation
        alert(f"Thank you! Your order {order_number} has been placed.")
        open_form('products.PublicCatalogForm')
      else:
        alert(f"Error: {result.get('error', 'Could not place order')}")

    except Exception as e:
      print(f"Error placing order: {e}")
      alert(f"Failed to place order: {str(e)}")

  @handle("btn_back", "click")
  def btn_back_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_next", "click")
  def btn_next_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
