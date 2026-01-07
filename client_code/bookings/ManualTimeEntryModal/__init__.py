from ._anvil_designer import ManualTimeEntryModalTemplate
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

class ManualTimeEntryModal(ManualTimeEntryModalTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Load dropdowns
    clients = anvil.server.call('get_all_customers')
    self.dd_client.items = [(c['email'].split('@')[0], c.get_id()) for c in clients]

    services = anvil.server.call('get_all_services')
    self.dd_service.items = [(s['service_name'], s.get_id()) for s in services]

    self.dp_date.date = datetime.now().date()
    self.txt_duration.placeholder = "Hours (e.g., 1.5)"
    self.txt_description.placeholder = "Description..."

  def save(self):
    """Save manual entry"""
    try:
      if not self.dd_client.selected_value or not self.dd_service.selected_value:
        alert("Client and service are required")
        return False

      duration_hours = float(self.txt_duration.text)
      duration_minutes = int(duration_hours * 60)

      entry_data = {
        'customer_id': self.dd_client.selected_value,
        'service_id': self.dd_service.selected_value,
        'start_time': datetime.combine(self.dp_date.date, datetime.min.time()),
        'end_time': datetime.combine(self.dp_date.date, datetime.min.time()),
        'duration_minutes': duration_minutes,
        'description': self.txt_description.text
      }

      result = anvil.server.call('save_time_entry', entry_data)
      return result['success']

    except Exception as e:
      alert(f"Error: {str(e)}")
      return False