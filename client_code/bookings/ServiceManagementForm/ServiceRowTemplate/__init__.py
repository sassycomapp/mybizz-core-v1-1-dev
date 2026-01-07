from ._anvil_designer import ServiceRowTemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class ServiceRowTemplate(ServiceRowTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    # Display service data
    self.lbl_name.text = self.item['service_name']
    self.lbl_name.bold = True

    self.lbl_duration.text = f"{self.item['duration_minutes']} min"

    self.lbl_price.text = f"${self.item['price']:.2f}"

    # Staff member
    if self.item.get('staff_id'):
      self.lbl_staff.text = self.item['staff_id']['email'].split('@')[0]
    else:
      self.lbl_staff.text = "Any staff"

    # Configure action links
    self.link_edit.text = "✏️ Edit"
    self.link_edit.role = "secondary-color"

    self.link_delete.text = "🗑️ Delete"
    self.link_delete.role = "danger"

  def link_edit_click(self, **event_args):
    """Edit this service"""
    result = alert(
      content=ServiceEditorModal(service_id=self.item.get_id()),
      title="Edit Service",
      large=False,
      buttons=[("Cancel", False), ("Save", True)]
    )

    if result:
      self.parent.raise_event('x-refresh-services')

  def link_delete_click(self, **event_args):
    """Delete this service"""
    if confirm(f"Delete service '{self.item['service_name']}'?"):
      try:
        anvil.server.call('delete_service', self.item.get_id())
        Notification("Service deleted successfully").show()
        self.parent.raise_event('x-refresh-services')
      except Exception as e:
        alert(f"Error deleting service: {str(e)}")