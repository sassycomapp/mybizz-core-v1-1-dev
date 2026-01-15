from ._anvil_designer import UpcomingAppointmentTemplateTemplate
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


class UpcomingAppointmentTemplate(UpcomingAppointmentTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    self.lbl_datetime.text = self.item['datetime'].strftime('%b %d, %Y @ %I:%M %p')
    self.lbl_datetime.bold = True

    self.lbl_description.text = f"{self.item['service_name']} with {self.item['staff_name']}"

    self.link_reschedule.text = "Reschedule"
    self.link_reschedule.role = "secondary-color"

    self.link_cancel.text = "Cancel"
    self.link_cancel.role = "danger"

  def link_reschedule_click(self, **event_args):
    """Reschedule appointment"""
    # TODO: Open reschedule form
    alert("Reschedule functionality coming soon")

  def link_cancel_click(self, **event_args):
    """Cancel appointment"""
    if confirm("Cancel this appointment?"):
      try:
        anvil.server.call('cancel_booking', self.item['booking_id'])
        Notification("Appointment cancelled").show()
        self.parent.parent.load_portal_data()
      except Exception as e:
        alert(f"Error: {str(e)}")