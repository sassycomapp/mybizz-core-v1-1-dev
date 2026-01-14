from ._anvil_designer import ReportsFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ReportsForm(ReportsFormTemplate):
  """Report generation dashboard"""

  def __init__(self, **properties):
    self.init_components(**properties)

    # Check permissions
    user = anvil.users.get_user()
    if not user or user['role'] not in ['owner', 'manager']:
      alert("Access denied")
      open_form('dashboard.DashboardForm')
      return

    # Configure title
    self.lbl_title.text = "Reports"
    self.lbl_title.font_size = 24
    self.lbl_title.bold = True

    # Configure section labels
    self.lbl_report_type.text = "Report Type:"
    self.lbl_report_type.font_size = 16
    self.lbl_report_type.bold = True

    self.lbl_date_range.text = "Date Range:"
    self.lbl_date_range.font_size = 16
    self.lbl_date_range.bold = True

    self.lbl_start_date.text = "From:"
    self.lbl_end_date.text = "To:"

    self.lbl_filters.text = "Filters (optional):"
    self.lbl_filters.font_size = 16
    self.lbl_filters.bold = True

    self.lbl_preview_header.text = "Report Preview:"
    self.lbl_preview_header.font_size = 16
    self.lbl_preview_header.bold = True

    # Configure report type dropdown
    self.dd_report_type.items = [
      ('Sales Report', 'sales'),
      ('Customer Report', 'customer'),
      ('Booking Report', 'booking'),
      ('Financial Summary', 'financial'),
      ('Tax Report', 'tax')
    ]
    self.dd_report_type.selected_value = 'sales'

    # Configure date range (default to current year)
    today = datetime.now()
    start_of_year = today.replace(month=1, day=1)

    self.dp_start_date.date = start_of_year
    self.dp_end_date.date = today

    # Configure filter dropdowns
    self.dd_category_filter.items = [
      ('All Categories', 'all'),
      ('Products', 'products'),
      ('Services', 'services'),
      ('Bookings', 'bookings')
    ]
    self.dd_category_filter.selected_value = 'all'

    self.dd_status_filter.items = [
      ('All Statuses', 'all'),
      ('Active', 'active'),
      ('Completed', 'completed'),
      ('Cancelled', 'cancelled')
    ]
    self.dd_status_filter.selected_value = 'all'

    # Configure buttons
    self.btn_generate.text = "Generate Report"
    self.btn_generate.icon = "fa:file-text"
    self.btn_generate.role = "primary-color"

    self.btn_export_pdf.text = "Export to PDF"
    self.btn_export_pdf.icon = "fa:file-pdf-o"
    self.btn_export_pdf.role = "outlined-button"
    self.btn_export_pdf.visible = False  # Hidden until report generated

  def button_generate_click(self, **event_args):
    """Generate report"""
    report_type = self.dd_report_type.selected_value
    start_date = self.dp_start_date.date
    end_date = self.dp_end_date.date

    # Validate dates
    if not start_date or not end_date:
      alert("Please select date range")
      return

    if start_date > end_date:
      alert("Start date must be before end date")
      return

    # Get filter values
    category = self.dd_category_filter.selected_value
    status = self.dd_status_filter.selected_value

    try:
      # Generate report based on type
      filters = {
        'category': category,
        'status': status
      }

      if report_type == 'sales':
        result = anvil.server.call('generate_sales_report', start_date, end_date, filters)
      elif report_type == 'customer':
        result = anvil.server.call('generate_customer_report', start_date, end_date, filters)
      elif report_type == 'booking':
        result = anvil.server.call('generate_booking_report', start_date, end_date, filters)
      elif report_type == 'financial':
        result = anvil.server.call('generate_financial_summary', start_date, end_date, filters)
      elif report_type == 'tax':
        result = anvil.server.call('generate_tax_report', start_date.year, 1, filters)  # Q1

      if result['success']:
        # Display report
        self.display_report(result['report'])
        self.btn_export_pdf.visible = True
        Notification("Report generated!", style="success").show()
      else:
        alert(f"Error: {result.get('error')}")
        self.btn_export_pdf.visible = False

    except Exception as e:
      print(f"Error generating report: {e}")
      alert(f"Failed to generate report: {str(e)}")
      self.btn_export_pdf.visible = False

  def display_report(self, report_data):
    """Display generated report"""
    # Clear preview area
    self.col_preview.clear()

    # Add report title
    lbl_report_title = Label(
      text=report_data.get('title', 'Report'),
      font_size=20,
      bold=True
    )
    self.col_preview.add_component(lbl_report_title)

    # Add date range
    lbl_date_range = Label(
      text=f"Period: {report_data.get('start_date')} to {report_data.get('end_date')}",
      foreground="#666666",
      font_size=14
    )
    self.col_preview.add_component(lbl_date_range)

    # Add summary metrics
    if report_data.get('summary'):
      lbl_summary_header = Label(
        text="Summary",
        font_size=16,
        bold=True,
        spacing_above='medium'
      )
      self.col_preview.add_component(lbl_summary_header)

      for metric, value in report_data['summary'].items():
        lbl_metric = Label(
          text=f"{metric}: {value}",
          font_size=14
        )
        self.col_preview.add_component(lbl_metric)

    # Add data table
    if report_data.get('data'):
      lbl_data_header = Label(
        text="Detailed Data",
        font_size=16,
        bold=True,
        spacing_above='medium'
      )
      self.col_preview.add_component(lbl_data_header)

      dg_data = DataGrid(
        auto_header=True,
        rows_per_page=20
      )
      dg_data.items = report_data['data']
      self.col_preview.add_component(dg_data)

  def button_export_pdf_click(self, **event_args):
    """Export report to PDF"""
    try:
      report_type = self.dd_report_type.selected_value
      start_date = self.dp_start_date.date
      end_date = self.dp_end_date.date

      category = self.dd_category_filter.selected_value
      status = self.dd_status_filter.selected_value

      filters = {
        'category': category,
        'status': status
      }

      result = anvil.server.call('export_report_pdf', report_type, start_date, end_date, filters)

      if result['success']:
        # Download PDF
        anvil.media.download(result['pdf_file'])
        Notification("PDF downloaded!", style="success").show()
      else:
        alert(f"Export failed: {result.get('error')}")

    except Exception as e:
      print(f"Error exporting PDF: {e}")
      alert(f"Failed to export: {str(e)}")

  @handle("btn_generate", "click")
  def btn_generate_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_export_pdf", "click")
  def btn_export_pdf_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
