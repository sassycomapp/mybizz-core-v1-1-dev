import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.stripe
import anvil.secrets
import anvil.files
from anvil.files import data_files
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

from datetime import datetime
from anvil.pdf import PDFRenderer
import io

@anvil.server.callable
@anvil.users.login_required
def generate_sales_report(start_date, end_date, filters):
  """
  Generate sales report.
  
  Args:
    start_date (date): Report start date
    end_date (date): Report end date
    filters (dict): Additional filters (category, status)
    
  Returns:
    dict: {'success': bool, 'report': dict} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    # Query sales data
    query = {
      'created_at': q.between(start_date, end_date, min_inclusive=True, max_inclusive=True)
    }

    # Add status filter
    if filters.get('status') and filters['status'] != 'all':
      query['status'] = filters['status']

    orders = list(app_tables.orders.search(**query))

    # Calculate metrics
    total_revenue = sum(o.get('total_amount', 0) for o in orders)
    total_orders = len(orders)
    avg_order = total_revenue / total_orders if total_orders > 0 else 0

    # Build report
    report = {
      'title': 'Sales Report',
      'start_date': start_date.strftime('%Y-%m-%d'),
      'end_date': end_date.strftime('%Y-%m-%d'),
      'summary': {
        'Total Revenue': f"${total_revenue:,.2f}",
        'Total Orders': total_orders,
        'Average Order': f"${avg_order:,.2f}"
      },
      'data': [
        {
          'Order #': o.get('order_number', 'N/A'),
          'Date': o['created_at'].strftime('%Y-%m-%d'),
          'Customer': o['customer_id']['email'] if o.get('customer_id') else 'Guest',
          'Status': o.get('status', 'unknown'),
          'Total': f"${o.get('total_amount', 0):,.2f}"
        }
        for o in orders
      ]
    }

    return {'success': True, 'report': report}

  except Exception as e:
    print(f"Error generating sales report: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
@anvil.users.login_required
def generate_customer_report(start_date, end_date, filters):
  """
  Generate customer report.
  
  Args:
    start_date (date): Report start date
    end_date (date): Report end date
    filters (dict): Additional filters
    
  Returns:
    dict: {'success': bool, 'report': dict} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    # Get customers registered in date range
    customers = list(app_tables.users.search(
      role='customer',
      created_at=q.between(start_date, end_date, min_inclusive=True, max_inclusive=True)
    ))

    total_customers = len(customers)

    # Calculate customer metrics
    active_customers = len([c for c in customers if c.get('is_active', True)])

    report = {
      'title': 'Customer Report',
      'start_date': start_date.strftime('%Y-%m-%d'),
      'end_date': end_date.strftime('%Y-%m-%d'),
      'summary': {
        'Total Customers': total_customers,
        'Active Customers': active_customers
      },
      'data': [
        {
          'Email': c['email'],
          'Name': c.get('name', 'N/A'),
          'Registered': c['created_at'].strftime('%Y-%m-%d'),
          'Status': 'Active' if c.get('is_active', True) else 'Inactive'
        }
        for c in customers
      ]
    }

    return {'success': True, 'report': report}

  except Exception as e:
    print(f"Error generating customer report: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
@anvil.users.login_required
def generate_booking_report(start_date, end_date, filters):
  """
  Generate booking report.
  
  Args:
    start_date (date): Report start date
    end_date (date): Report end date
    filters (dict): Additional filters
    
  Returns:
    dict: {'success': bool, 'report': dict} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    # Query bookings
    query = {
      'booking_date': q.between(start_date, end_date, min_inclusive=True, max_inclusive=True)
    }

    if filters.get('status') and filters['status'] != 'all':
      query['status'] = filters['status']

    bookings = list(app_tables.bookings.search(**query))

    total_bookings = len(bookings)
    confirmed = len([b for b in bookings if b.get('status') == 'confirmed'])
    cancelled = len([b for b in bookings if b.get('status') == 'cancelled'])

    report = {
      'title': 'Booking Report',
      'start_date': start_date.strftime('%Y-%m-%d'),
      'end_date': end_date.strftime('%Y-%m-%d'),
      'summary': {
        'Total Bookings': total_bookings,
        'Confirmed': confirmed,
        'Cancelled': cancelled
      },
      'data': [
        {
          'Booking ID': b.get_id(),
          'Date': b['booking_date'].strftime('%Y-%m-%d'),
          'Customer': b['customer_id']['email'] if b.get('customer_id') else 'N/A',
          'Status': b.get('status', 'unknown')
        }
        for b in bookings
      ]
    }

    return {'success': True, 'report': report}

  except Exception as e:
    print(f"Error generating booking report: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
@anvil.users.login_required
def generate_financial_summary(start_date, end_date, filters):
  """
  Generate financial summary.
  
  Args:
    start_date (date): Report start date
    end_date (date): Report end date
    filters (dict): Additional filters
    
  Returns:
    dict: {'success': bool, 'report': dict} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    # Get all transactions
    transactions = list(app_tables.transactions.search(
      created_at=q.between(start_date, end_date, min_inclusive=True, max_inclusive=True)
    ))

    total_income = sum(t['amount'] for t in transactions if t['amount'] > 0)
    total_expenses = sum(abs(t['amount']) for t in transactions if t['amount'] < 0)
    net_profit = total_income - total_expenses

    report = {
      'title': 'Financial Summary',
      'start_date': start_date.strftime('%Y-%m-%d'),
      'end_date': end_date.strftime('%Y-%m-%d'),
      'summary': {
        'Total Income': f"${total_income:,.2f}",
        'Total Expenses': f"${total_expenses:,.2f}",
        'Net Profit': f"${net_profit:,.2f}"
      },
      'data': [
        {
          'Date': t['created_at'].strftime('%Y-%m-%d'),
          'Description': t.get('description', 'N/A'),
          'Type': 'Income' if t['amount'] > 0 else 'Expense',
          'Amount': f"${abs(t['amount']):,.2f}"
        }
        for t in transactions
      ]
    }

    return {'success': True, 'report': report}

  except Exception as e:
    print(f"Error generating financial summary: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
@anvil.users.login_required
def generate_tax_report(year, quarter, filters):
  """
  Generate tax report.
  
  Args:
    year (int): Tax year
    quarter (int): Tax quarter (1-4)
    filters (dict): Additional filters
    
  Returns:
    dict: {'success': bool, 'report': dict} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    # Calculate quarter dates
    quarter_months = {
      1: (1, 3),
      2: (4, 6),
      3: (7, 9),
      4: (10, 12)
    }

    start_month, end_month = quarter_months[quarter]
    start_date = datetime(year, start_month, 1)
    end_date = datetime(year, end_month, 28)  # Simplified

    # Get taxable transactions
    transactions = list(app_tables.transactions.search(
      created_at=q.between(start_date, end_date, min_inclusive=True, max_inclusive=True),
      taxable=True
    ))

    taxable_income = sum(t['amount'] for t in transactions if t['amount'] > 0)
    tax_rate = 0.21  # Example rate
    estimated_tax = taxable_income * tax_rate

    report = {
      'title': f'Tax Report - Q{quarter} {year}',
      'start_date': start_date.strftime('%Y-%m-%d'),
      'end_date': end_date.strftime('%Y-%m-%d'),
      'summary': {
        'Taxable Income': f"${taxable_income:,.2f}",
        'Tax Rate': f"{tax_rate * 100}%",
        'Estimated Tax': f"${estimated_tax:,.2f}"
      },
      'data': [
        {
          'Date': t['created_at'].strftime('%Y-%m-%d'),
          'Description': t.get('description', 'N/A'),
          'Amount': f"${t['amount']:,.2f}",
          'Tax': f"${t['amount'] * tax_rate:,.2f}"
        }
        for t in transactions
      ]
    }

    return {'success': True, 'report': report}

  except Exception as e:
    print(f"Error generating tax report: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
@anvil.users.login_required
def export_report_pdf(report_type, start_date, end_date, filters):
  """
  Export report to PDF.
  
  Args:
    report_type (str): Report type
    start_date (date): Report start date
    end_date (date): Report end date
    filters (dict): Additional filters
    
  Returns:
    dict: {'success': bool, 'pdf_file': Media} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    # Generate report first
    if report_type == 'sales':
      result = generate_sales_report(start_date, end_date, filters)
    elif report_type == 'customer':
      result = generate_customer_report(start_date, end_date, filters)
    elif report_type == 'booking':
      result = generate_booking_report(start_date, end_date, filters)
    elif report_type == 'financial':
      result = generate_financial_summary(start_date, end_date, filters)
    else:
      return {'success': False, 'error': 'Invalid report type'}

    if not result['success']:
      return result

    report = result['report']

    # Generate PDF (simplified - you'd use PDFRenderer or ReportLab)
    pdf_html = f"""
    <html>
      <body>
        <h1>{report['title']}</h1>
        <p>Period: {report['start_date']} to {report['end_date']}</p>
        <h2>Summary</h2>
        {''.join(f"<p>{k}: {v}</p>" for k, v in report['summary'].items())}
      </body>
    </html>
    """

    # Convert to PDF (requires PDF library)
    pdf_file = PDFRenderer(html=pdf_html).render_pdf()

    return {'success': True, 'pdf_file': pdf_file}

  except Exception as e:
    print(f"Error exporting PDF: {e}")
    return {'success': False, 'error': str(e)}