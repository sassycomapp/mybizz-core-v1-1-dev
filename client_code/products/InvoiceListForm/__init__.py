from ._anvil_designer import InvoiceListFormTemplate
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


class InvoiceListForm(InvoiceListFormTemplate):
  """Invoice management for orders and services"""

  def __init__(self, **properties):
    self.init_components(**properties)

    # Check authentication
    user = anvil.users.get_user()
    if not user:
      open_form('auth.LoginForm')
      return

    if user['role'] not in ['owner', 'manager']:
      alert("Access denied")
      open_form('dashboard.DashboardForm')
      return

    # Configure title
    self.lbl_title.text = "Invoices"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True

    # Configure new invoice button
    self.btn_new_invoice.text = "New Invoice"
    self.btn_new_invoice.icon = "fa:plus"
    self.btn_new_invoice.role = "primary-color"

    # Configure search
    self.txt_search.placeholder = "Search by invoice # or customer..."
    self.txt_search.icon = "fa:search"

    self.btn_search.text = ""
    self.btn_search.icon = "fa:search"
    self.btn_search.role = "secondary-color"

    # Configure filters
    self.dd_status_filter.items = [
      ('All Statuses', 'all'),
      ('Unpaid', 'unpaid'),
      ('Paid', 'paid'),
      ('Overdue', 'overdue')
    ]
    self.dd_status_filter.selected_value = 'all'

    # Configure data grid
    self.dg_invoices.columns = [
      {'id': 'invoice_number', 'title': 'Invoice #', 'data_key': 'invoice_number', 'width': 120},
      {'id': 'customer', 'title': 'Customer', 'data_key': 'customer_email', 'width': 200},
      {'id': 'amount', 'title': 'Amount', 'data_key': 'amount_display', 'width': 100},
      {'id': 'status', 'title': 'Status', 'data_key': 'status_display', 'width': 100},
      {'id': 'date', 'title': 'Date', 'data_key': 'date_display', 'width': 100},
      {'id': 'actions', 'title': 'Actions', 'data_key': None, 'width': 150}
    ]

    # Load invoices
    self.load_invoices()

  def load_invoices(self):
    """Load invoices (generated from orders)"""
    try:
      filters = {
        'search': self.txt_search.text,
        'status': self.dd_status_filter.selected_value
      }

      result = anvil.server.call('get_all_invoices', filters)

      if result['success']:
        invoices = result['data']

        # Add display fields
        for invoice in invoices:
          invoice['invoice_number'] = invoice['order_number'].replace('ORD', 'INV')
          invoice['amount_display'] = f"${invoice['total_amount']:.2f}"
          invoice['customer_email'] = invoice['customer_id']['email'] if invoice.get('customer_id') else 'Guest'

          # Status display
          if invoice['payment_status'] == 'paid':
            invoice['status_display'] = '✅ Paid'
          else:
            invoice['status_display'] = '❌ Unpaid'

          invoice['date_display'] = invoice['created_at'].strftime('%b %d')

        self.dg_invoices.items = invoices

        # Update stats
        total = len(invoices)
        unpaid = len([i for i in invoices if i['payment_status'] != 'paid'])
        outstanding = sum(i['total_amount'] for i in invoices if i['payment_status'] != 'paid')

        self.lbl_stats.text = f"Total: {total} invoices  •  Unpaid: {unpaid}  •  Outstanding: ${outstanding:.2f}"

      else:
        alert(f"Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
      print(f"Error loading invoices: {e}")
      alert(f"Failed to load invoices: {str(e)}")

  def button_new_invoice_click(self, **event_args):
    """Create new manual invoice"""
    alert("Manual invoice creation coming soon!")

  def button_search_click(self, **event_args):
    """Search invoices"""
    self.load_invoices()

  def dropdown_status_filter_change(self, **event_args):
    """Filter by status"""
    self.load_invoices()