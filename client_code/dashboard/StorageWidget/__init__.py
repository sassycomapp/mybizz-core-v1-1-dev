from ._anvil_designer import StorageWidgetTemplate
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


class StorageWidget(StorageWidgetTemplate):
  """Storage usage monitoring widget for Anvil plan limits"""

  def __init__(self, **properties):
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "Storage Usage"
    self.lbl_title.font_size = 18
    self.lbl_title.bold = True

    # Configure refresh button
    self.btn_refresh.text = ""
    self.btn_refresh.icon = "fa:refresh"
    self.btn_refresh.role = "outlined-button"

    # Configure labels
    self.lbl_db_label.text = "Database Rows"
    self.lbl_db_label.bold = True

    self.lbl_media_label.text = "Media Storage"
    self.lbl_media_label.bold = True

    # Configure progress bars
    self.progress_db.width = "100%"
    self.progress_media.width = "100%"

    # Configure warning label
    self.lbl_warning.visible = False
    self.lbl_warning.background = "#FFF3CD"
    self.lbl_warning.foreground = "#856404"
    self.lbl_warning.align = "center"
    self.lbl_warning.bold = True

    # Configure detailed report button
    self.btn_detailed_report.text = "View Detailed Report"
    self.btn_detailed_report.role = "outlined-button"

    # Load storage data
    self.load_storage_usage()

  def load_storage_usage(self):
    """Load and display storage usage"""
    try:
      # Get storage data from server
      result = anvil.server.call('get_storage_usage')

      if result['success']:
        data = result['data']

        # Database usage
        db_rows = data['database_rows']
        db_limit = data['database_limit']
        db_percent = (db_rows / db_limit * 100) if db_limit > 0 else 0

        self.progress_db.progress = db_percent / 100
        self.lbl_db_stats.text = f"{db_rows:,} / {db_limit:,} rows ({db_percent:.1f}%)"

        # Set progress bar color based on usage
        if db_percent >= 95:
          self.progress_db.foreground = "red"
        elif db_percent >= 80:
          self.progress_db.foreground = "orange"
        else:
          self.progress_db.foreground = "green"

        # Media usage
        media_bytes = data['media_bytes']
        media_limit = data['media_limit_bytes']
        media_gb = media_bytes / (1024 ** 3)
        media_limit_gb = media_limit / (1024 ** 3)
        media_percent = (media_bytes / media_limit * 100) if media_limit > 0 else 0

        self.progress_media.progress = media_percent / 100
        self.lbl_media_stats.text = f"{media_gb:.2f} GB / {media_limit_gb:.0f} GB ({media_percent:.1f}%)"

        # Set progress bar color based on usage
        if media_percent >= 95:
          self.progress_media.foreground = "red"
        elif media_percent >= 80:
          self.progress_media.foreground = "orange"
        else:
          self.progress_media.foreground = "green"

        # Show warning if approaching limits
        warnings = []
        if db_percent >= 80:
          warnings.append(f"Database at {db_percent:.0f}%")
        if media_percent >= 80:
          warnings.append(f"Media storage at {media_percent:.0f}%")

        if warnings:
          self.lbl_warning.text = "⚠️  Warning: " + ", ".join(warnings)
          self.lbl_warning.visible = True
        else:
          self.lbl_warning.visible = False

      else:
        alert(f"Error loading storage: {result.get('error', 'Unknown error')}")

    except Exception as e:
      print(f"Error loading storage usage: {e}")
      alert(f"Failed to load storage data: {str(e)}")

  def button_refresh_click(self, **event_args):
    """Refresh storage usage"""
    self.load_storage_usage()

  def button_detailed_report_click(self, **event_args):
    """Show detailed storage breakdown"""
    try:
      result = anvil.server.call('get_detailed_storage_report')

      if result['success']:
        report = result['data']

        # Format report for display
        report_text = "Storage Breakdown:\n\n"

        for table_name, row_count in report.get('table_counts', {}).items():
          report_text += f"{table_name}: {row_count:,} rows\n"

        report_text += f"\nTotal: {report.get('total_rows', 0):,} rows"

        alert(report_text, title="Detailed Storage Report", large=True)
      else:
        alert(f"Error: {result.get('error', 'Could not generate report')}")

    except Exception as e:
      print(f"Error getting detailed report: {e}")
      alert(f"Failed to generate report: {str(e)}")

  @handle("btn_refresh", "click")
  def btn_refresh_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_detailed_report", "click")
  def btn_detailed_report_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
