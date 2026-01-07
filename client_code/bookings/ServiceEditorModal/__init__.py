from ._anvil_designer import ServiceEditorModalTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class ServiceEditorModal(ServiceEditorModalTemplate):
  def __init__(self, service_id=None, **properties):
    self.service_id = service_id
    self.init_components(**properties)

    # Configure labels
    self.lbl_name_field.text = "Service Name *"
    self.lbl_name_field.bold = True

    self.lbl_duration_field.text = "Duration (minutes) *"
    self.lbl_duration_field.bold = True

    self.lbl_price_field.text = "Price *"
    self.lbl_price_field.bold = True

    self.lbl_staff_field.text = "Staff Member"
    self.lbl_staff_field.bold = True

    self.lbl_description_field.text = "Description"
    self.lbl_description_field.bold = True

    # Configure fields
    self.txt_service_name.placeholder = "e.g., Consultation, Therapy Session"

    self.txt_duration.type = "number"
    self.txt_duration.placeholder = "60"

    self.txt_price.type = "number"
    self.txt_price.placeholder = "0.00"

    # Load staff members
    self.load_staff()

    self.txt_description.placeholder = "Service description..."
    self.txt_description.rows = 3

    # Load existing service if editing
    if self.service_id:
      self.load_service()

  def load_staff(self):
    """Load staff members"""
    try:
      staff = anvil.server.call('get_staff_members')
      self.dd_staff.items = [('Any staff member', None)] + [
        (s['email'].split('@')[0], s.get_id()) for s in staff
      ]
      self.dd_staff.selected_value = None
    except Exception as e:
      print(f"Error loading staff: {e}")

  def load_service(self):
    """Load existing service"""
    try:
      service = anvil.server.call('get_service', self.service_id)
      if service:
        self.txt_service_name.text = service['service_name']
        self.txt_duration.text = str(service['duration_minutes'])
        self.txt_price.text = str(service['price'])
        if service.get('staff_id'):
          self.dd_staff.selected_value = service['staff_id'].get_id()
        self.txt_description.text = service.get('description', '')
    except Exception as e:
      alert(f"Error loading service: {str(e)}")

  def save(self):
    """Save service (called when user clicks Save button)"""
    try:
      if not self.txt_service_name.text:
        alert("Service name is required")
        return False

      if not self.txt_duration.text:
        alert("Duration is required")
        return False

      if not self.txt_price.text:
        alert("Price is required")
        return False

      service_data = {
        'service_name': self.txt_service_name.text,
        'duration_minutes': int(self.txt_duration.text),
        'price': float(self.txt_price.text),
        'staff_id': self.dd_staff.selected_value,
        'description': self.txt_description.text
      }

      result = anvil.server.call(
        'save_service',
        self.service_id,
        service_data
      )

      if result['success']:
        return True
      else:
        alert(result['error'])
        return False

    except Exception as e:
      alert(f"Error saving service: {str(e)}")
      return False