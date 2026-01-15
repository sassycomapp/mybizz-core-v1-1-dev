from ._anvil_designer import DocumentTemplateTemplate
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


class DocumentTemplate(DocumentTemplateTemplate):
  def __init__(self, **properties):
    self.item = properties.get('item')
    self.init_components(**properties)

    shared_date = self.item['shared_date'].strftime('%b %d')
    self.lbl_document.text = f"📄 {self.item['name']}  •  Shared {shared_date}"

    self.link_download.text = "Download"
    self.link_download.role = "secondary-color"

  def link_download_click(self, **event_args):
    """Download document"""
    # Download actual file
    anvil.media.download(self.item['file'])