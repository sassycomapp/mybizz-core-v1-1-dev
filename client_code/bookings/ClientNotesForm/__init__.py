from ._anvil_designer import ClientNotesFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class ClientNotesForm(ClientNotesFormTemplate):
  def __init__(self, customer_id=None, **properties):
    self.customer_id = customer_id
    self.customer = None
    self.init_components(**properties)

    # Configure back link
    self.link_back.text = "← Back"
    self.link_back.role = "secondary-color"

    # Configure title
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True
    self.lbl_title.role = "headline"

    # Configure privacy notice
    self.lbl_privacy_notice.text = "🔒 Confidential - Staff Only"
    self.lbl_privacy_notice.background = "#FFF3CD"
    self.lbl_privacy_notice.foreground = "#856404"
    self.lbl_privacy_notice.align = "center"
    self.lbl_privacy_notice.bold = True

    # Configure repeating panel
    self.rp_notes.item_template = 'bookings.ClientNoteTemplate'

    # Configure no notes label
    self.lbl_no_notes.text = "No notes yet for this client"
    self.lbl_no_notes.align = "center"
    self.lbl_no_notes.foreground = "#666666"
    self.lbl_no_notes.visible = False

    # Configure add note section
    self.lbl_add_note_section.text = "ADD NEW NOTE"
    self.lbl_add_note_section.bold = True
    self.lbl_add_note_section.font_size = 16

    # Configure note textarea
    self.txt_new_note.placeholder = "Write your note here..."
    self.txt_new_note.rows = 5

    # Configure confidential checkbox
    self.cb_confidential.text = "Confidential (visible to managers only)"

    # Configure add button
    self.btn_add_note.text = "Add Note"
    self.btn_add_note.icon = "fa:plus"
    self.btn_add_note.role = "primary-color"

    # Load customer and notes
    if self.customer_id:
      self.load_customer()
      self.load_notes()

  def load_customer(self):
    """Load customer details"""
    try:
      self.customer = anvil.server.call('get_customer', self.customer_id)
      if self.customer:
        customer_name = self.customer['email'].split('@')[0]
        self.lbl_title.text = f"Client Notes: {customer_name}"
    except Exception as e:
      alert(f"Error loading customer: {str(e)}")

  def load_notes(self):
    """Load all notes for this customer"""
    try:
      notes = anvil.server.call('get_client_notes', self.customer_id)

      if notes:
        self.rp_notes.items = notes
        self.rp_notes.visible = True
        self.lbl_no_notes.visible = False
      else:
        self.rp_notes.visible = False
        self.lbl_no_notes.visible = True

    except Exception as e:
      alert(f"Error loading notes: {str(e)}")

  def button_add_note_click(self, **event_args):
    """Add new note"""
    try:
      if not self.txt_new_note.text or len(self.txt_new_note.text) < 5:
        alert("Please write at least 5 characters")
        return

      note_data = {
        'customer_id': self.customer_id,
        'note': self.txt_new_note.text,
        'is_confidential': self.cb_confidential.checked
      }

      result = anvil.server.call('add_client_note', note_data)

      if result['success']:
        Notification("Note added successfully", style="success").show()
        self.txt_new_note.text = ""
        self.cb_confidential.checked = False
        self.load_notes()
      else:
        alert(result['error'])

    except Exception as e:
      alert(f"Error adding note: {str(e)}")

  @handle("link_back", "click")
  def link_back_click(self, **event_args):
    """Navigate back"""
    open_form('bookings.BookingListForm')

  @handle("btn_add_note", "click")
  def btn_add_note_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
