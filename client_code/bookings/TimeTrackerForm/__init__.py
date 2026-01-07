from ._anvil_designer import TimeTrackerFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime

class TimeTrackerForm(TimeTrackerFormTemplate):
  def __init__(self, **properties):
    self.timer_running = False
    self.start_time = None
    self.timer_interval = None
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "Time Tracker"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True
    self.lbl_title.role = "headline"

    # Configure manual entry button
    self.btn_manual.text = "Manual Entry"
    self.btn_manual.icon = "fa:pencil"
    self.btn_manual.role = "secondary-color"

    # Configure timer section
    self.lbl_timer_section.text = "ACTIVE TIMER"
    self.lbl_timer_section.bold = True
    self.lbl_timer_section.font_size = 16

    self.lbl_client_field.text = "Client"
    self.lbl_client_field.bold = True

    self.dd_client.placeholder = "Select client..."
    self.load_clients()

    self.lbl_service_field.text = "Service"
    self.lbl_service_field.bold = True

    self.dd_service.placeholder = "Select service..."
    self.load_services()

    self.lbl_description_field.text = "Description"
    self.lbl_description_field.bold = True

    self.txt_description.placeholder = "What are you working on..."

    # Configure timer display
    self.lbl_timer.text = "⏱️  00:00:00"
    self.lbl_timer.font_size = 32
    self.lbl_timer.bold = True
    self.lbl_timer.align = "center"

    # Configure timer buttons
    self.btn_start_timer.text = "▶️ Start Timer"
    self.btn_start_timer.icon = "fa:play"
    self.btn_start_timer.role = "primary-color"

    self.btn_stop_timer.text = "⏸️ Stop Timer"
    self.btn_stop_timer.icon = "fa:stop"
    self.btn_stop_timer.role = "danger"
    self.btn_stop_timer.visible = False

    # Configure entries section
    self.lbl_entries_section.text = "TIME ENTRIES"
    self.lbl_entries_section.bold = True
    self.lbl_entries_section.font_size = 16

    # Configure repeating panel
    self.rp_entries.item_template = 'bookings.TimeEntryTemplate'

    # Configure total
    self.lbl_total_unbilled.font_size = 18
    self.lbl_total_unbilled.bold = True

    # Load entries
    self.load_entries()

  def load_clients(self):
    """Load clients"""
    try:
      clients = anvil.server.call('get_all_customers')
      self.dd_client.items = [
        (c['email'].split('@')[0], c.get_id()) for c in clients
      ]
    except Exception as e:
      print(f"Error loading clients: {e}")

  def load_services(self):
    """Load services"""
    try:
      services = anvil.server.call('get_all_services')
      self.dd_service.items = [
        (s['service_name'], s.get_id()) for s in services
      ]
    except Exception as e:
      print(f"Error loading services: {e}")

  def load_entries(self):
    """Load time entries"""
    try:
      entries = anvil.server.call('get_time_entries')
      self.rp_entries.items = entries

      # Calculate total unbilled
      total = sum(e['total_amount'] for e in entries if not e.get('invoiced', False))
      self.lbl_total_unbilled.text = f"Total Unbilled: ${total:.2f}"

    except Exception as e:
      alert(f"Error loading entries: {str(e)}")

  def button_start_timer_click(self, **event_args):
    """Start timer"""
    if not self.dd_client.selected_value:
      alert("Please select a client")
      return

    if not self.dd_service.selected_value:
      alert("Please select a service")
      return

    # Start timer
    self.timer_running = True
    self.start_time = datetime.now()

    # Show/hide buttons
    self.btn_start_timer.visible = False
    self.btn_stop_timer.visible = True

    # Start timer update
    self.timer_interval = anvil.server.call('start_timer_task')
    self.update_timer()

  def update_timer(self):
    """Update timer display"""
    if self.timer_running and self.start_time:
      elapsed = datetime.now() - self.start_time
      hours = int(elapsed.total_seconds() // 3600)
      minutes = int((elapsed.total_seconds() % 3600) // 60)
      seconds = int(elapsed.total_seconds() % 60)

      self.lbl_timer.text = f"⏱️  {hours:02d}:{minutes:02d}:{seconds:02d}"

      # Schedule next update
      anvil.js.window.setTimeout(self.update_timer, 1000)

  def button_stop_timer_click(self, **event_args):
    """Stop timer and save entry"""
    if not self.timer_running:
      return

    # Stop timer
    self.timer_running = False
    end_time = datetime.now()
    elapsed = end_time - self.start_time
    duration_minutes = int(elapsed.total_seconds() / 60)

    # Show/hide buttons
    self.btn_start_timer.visible = True
    self.btn_stop_timer.visible = False
    self.lbl_timer.text = "⏱️  00:00:00"

    # Save entry
    try:
      entry_data = {
        'customer_id': self.dd_client.selected_value,
        'service_id': self.dd_service.selected_value,
        'start_time': self.start_time,
        'end_time': end_time,
        'duration_minutes': duration_minutes,
        'description': self.txt_description.text
      }

      result = anvil.server.call('save_time_entry', entry_data)

      if result['success']:
        Notification("Time entry saved", style="success").show()
        # Clear form
        self.txt_description.text = ""
        self.load_entries()
      else:
        alert(result['error'])

    except Exception as e:
      alert(f"Error saving entry: {str(e)}")

  def button_manual_click(self, **event_args):
    """Open manual entry modal"""
    result = alert(
      content=ManualTimeEntryModal(),
      title="Manual Time Entry",
      large=False,
      buttons=[("Cancel", False), ("Save", True)]
    )

    if result:
      self.load_entries()