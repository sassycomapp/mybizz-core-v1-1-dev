from ._anvil_designer import InvoiceTemplateTemplate
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


class InvoiceTemplate(InvoiceTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    date = self.item['date'].strftime('%b %d, %Y')
    amount = f"${self.item['amount']:.2f}"
    status = self.item['status'].capitalize()

    self.lbl_invoice.text = f"{self.item['number']}  •  {date}  •  {amount}  •  {status}"

    self.link_download.text = "📄 Download"
    self.link_download.role = "secondary-color"

  def link_download_click(self, **event_args):
    """Download invoice"""
    # TODO: Generate PDF
    alert("Invoice download coming soon")