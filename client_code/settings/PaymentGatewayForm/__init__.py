from ._anvil_designer import PaymentGatewayFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class PaymentGatewayForm(PaymentGatewayFormTemplate):
  """Payment gateway selection form"""

  def __init__(self, **properties):
    self.init_components(**properties)

    self.lbl_title.text = "Payment Gateway Selection"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True

    self.lbl_info.text = "Choose your payment gateway based on your primary market.\n⚠️ This cannot be changed later."
    self.lbl_info.foreground = "#FF9800"

    # Stripe option
    self.rb_stripe.text = "Stripe"
    self.rb_stripe.group_name = "gateway"

    self.lbl_stripe_desc.text = "Recommended for: USA, Europe, Global\nSupports: Credit cards, Apple Pay, Google Pay"
    self.lbl_stripe_desc.foreground = "#666666"

    # Paystack option
    self.rb_paystack.text = "Paystack"
    self.rb_paystack.group_name = "gateway"

    self.lbl_paystack_desc.text = "Recommended for: Nigeria, South Africa, Ghana, Kenya\nSupports: Cards, Mobile money, Bank transfer"
    self.lbl_paystack_desc.foreground = "#666666"

    # PayPal option
    self.rb_paypal.text = "PayPal (Future)"
    self.rb_paypal.group_name = "gateway"
    self.rb_paypal.enabled = False

    self.lbl_paypal_desc.text = "One-time payments only (Coming soon)"
    self.lbl_paypal_desc.foreground = "#999999"

    # Continue button
    self.btn_continue.text = "Continue"
    self.btn_continue.icon = "fa:arrow-right"
    self.btn_continue.role = "primary-color"

  def button_continue_click(self, **event_args):
    """Save gateway selection"""
    gateway = None

    if self.rb_stripe.selected:
      gateway = 'stripe'
    elif self.rb_paystack.selected:
      gateway = 'paystack'
    elif self.rb_paypal.selected:
      gateway = 'paypal'

    if not gateway:
      alert("Please select a payment gateway")
      return

    try:
      result = anvil.server.call('select_payment_gateway', gateway)

      if result['success']:
        Notification(f"{gateway.title()} selected!", style="success").show()
        # Open API key configuration
        self.show_api_key_form(gateway)
      else:
        alert(f"Error: {result.get('error')}")

    except Exception as e:
      alert(f"Failed to save: {str(e)}")

  def show_api_key_form(self, gateway):
    """Show API key configuration"""
    if gateway == 'stripe':
      api_key = prompt("Enter your Stripe Secret Key:")
      if api_key:
        result = anvil.server.call('save_stripe_api_key', api_key)
        if result['success']:
          Notification("Stripe configured!", style="success").show()

    elif gateway == 'paystack':
      api_key = prompt("Enter your Paystack Secret Key:")
      if api_key:
        result = anvil.server.call('save_paystack_api_key', api_key)
        if result['success']:
          Notification("Paystack configured!", style="success").show()

  @handle("btn_continue", "click")
  def btn_continue_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
