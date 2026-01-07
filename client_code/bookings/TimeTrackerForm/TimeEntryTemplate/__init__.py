from ._anvil_designer import TimeEntryTemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class TimeEntryTemplate(TimeEntryTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    # Display data
    self.lbl_date.text = self.item['start_time'].strftime('%b %d')

    if self.item.get('customer_id'):
      self.lbl_client.text = self.item['customer_id']['email'].split('@')[0]
    else:
      self.lbl_client.text = "Unknown"

    if self.item.get('service_id'):
      self.lbl_service.text = self.item['service_id']['service_name']
    else:
      self.lbl_service.text = "Unknown"

    hours = self.item['duration_minutes'] / 60
    self.lbl_duration.text = f"{hours:.1f} hrs"

    self.lbl_rate.text = f"${self.item['hourly_rate']:.0f}"

    self.lbl_total.text = f"${self.item['total_amount']:.2f}"
    self.lbl_total.bold = True

    # Show invoiced status
    if self.item.get('invoiced', False):
      self.lbl_total.foreground = "#999999"

    self.link_delete.text = "🗑️"
    self.link_delete.role = "danger"

  def link_delete_click(self, **event_args):
    """Delete this entry"""
    if confirm("Delete this time entry?"):
      try:
        anvil.server.call('delete_time_entry', self.item.get_id())
        Notification("Entry deleted").show()
        self.parent.parent.load_entries()
      except Exception as e:
        alert(f"Error: {str(e)}")