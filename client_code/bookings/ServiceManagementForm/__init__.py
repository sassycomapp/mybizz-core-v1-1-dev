from ._anvil_designer import ServiceManagementFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class ServiceManagementForm(ServiceManagementFormTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "Service Management"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True
    self.lbl_title.role = "headline"

    # Configure add button
    self.btn_add_service.text = "Add Service"
    self.btn_add_service.icon = "fa:plus"
    self.btn_add_service.role = "primary-color"

    # Configure no services label
    self.lbl_no_services.text = "No services yet. Click 'Add Service' to create one!"
    self.lbl_no_services.align = "center"
    self.lbl_no_services.foreground = "#666666"
    self.lbl_no_services.visible = False

    # Set repeating panel template
    self.rp_services.item_template = 'bookings.ServiceRowTemplate'

    # Load services
    self.load_services()

  def load_services(self, **event_args):
    """Load all services"""
    try:
      services = anvil.server.call('get_all_services')

      if services:
        self.rp_services.items = services
        self.rp_services.visible = True
        self.lbl_no_services.visible = False
      else:
        self.rp_services.visible = False
        self.lbl_no_services.visible = True

    except Exception as e:
      alert(f"Error loading services: {str(e)}")

  def button_add_service_click(self, **event_args):
    """Open service editor modal"""
    result = alert(
      content=ServiceEditorModal(service_id=None),
      title="Add New Service",
      large=False,
      buttons=[("Cancel", False), ("Save", True)]
    )

    if result:
      self.load_services()

  @handle("btn_add_service", "click")
  def btn_add_service_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
