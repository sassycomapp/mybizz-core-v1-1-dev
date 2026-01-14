from ._anvil_designer import TicketSubmissionFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class TicketSubmissionForm(TicketSubmissionFormTemplate):
  """Public ticket submission form"""

  def __init__(self, **properties):
    self.attachments = []
    self.init_components(**properties)

    # Configure title
    self.lbl_title.text = "Submit a Support Ticket"
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True

    # Check if user is logged in
    user = anvil.users.get_user()

    if user:
      # Hide name/email for logged-in users
      self.txt_name.visible = False
      self.txt_email.visible = False
    else:
      # Show and configure for guest users
      self.txt_name.visible = True
      self.txt_name.placeholder = "Your Name"

      self.txt_email.visible = True
      self.txt_email.placeholder = "your@email.com"
      self.txt_email.type = "email"

    # Configure subject
    self.txt_subject.placeholder = "Brief description of the issue"

    # Configure category dropdown
    self.dd_category.items = [
      ('Select Category', None),
      ('Booking Issue', 'booking'),
      ('Payment Problem', 'payment'),
      ('Account Help', 'account'),
      ('Product Question', 'product'),
      ('Technical Issue', 'technical'),
      ('Other', 'other')
    ]
    self.dd_category.selected_value = None

    # Configure description
    self.txt_description.placeholder = "Please describe your issue in detail..."
    self.txt_description.rows = 6

    # Configure attachments
    self.lbl_attachments.text = "Attachments (max 3 files):"
    self.lbl_attachments.font_size = 14
    self.file_attachments.multiple = True

    # Configure submit button
    self.btn_submit.text = "Submit Ticket"
    self.btn_submit.icon = "fa:ticket"
    self.btn_submit.role = "primary-color"

  def file_loader_attachments_change(self, file, **event_args):
    """Handle file uploads"""
    if file:
      # Store files (can be multiple)
      if isinstance(file, list):
        self.attachments = file[:3]  # Max 3 files
      else:
        self.attachments = [file]

      # Show file names
      file_names = [f.name for f in self.attachments]
      Notification(f"Attached: {', '.join(file_names)}", style="info").show()

  def validate_form(self):
    """
    Validate form inputs.
    
    Returns:
      bool: True if valid
    """
    user = anvil.users.get_user()

    # Validate guest user fields
    if not user:
      if not self.txt_name.text or not self.txt_name.text.strip():
        alert("Please enter your name")
        return False

      if not self.txt_email.text or not self.txt_email.text.strip():
        alert("Please enter your email address")
        return False

      if '@' not in self.txt_email.text:
        alert("Please enter a valid email address")
        return False

    # Validate subject
    if not self.txt_subject.text or not self.txt_subject.text.strip():
      alert("Please enter a subject")
      return False

    # Validate category
    if not self.dd_category.selected_value:
      alert("Please select a category")
      return False

    # Validate description
    if not self.txt_description.text or not self.txt_description.text.strip():
      alert("Please describe your issue")
      return False

    return True

  def button_submit_click(self, **event_args):
    """Submit support ticket"""
    if not self.validate_form():
      return

    try:
      user = anvil.users.get_user()

      # Prepare customer data (for guest users)
      customer_data = None
      if not user:
        customer_data = {
          'name': self.txt_name.text.strip(),
          'email': self.txt_email.text.strip()
        }

      # Prepare ticket data
      ticket_data = {
        'subject': self.txt_subject.text.strip(),
        'category': self.dd_category.selected_value,
        'description': self.txt_description.text.strip(),
        'attachments': self.attachments if self.attachments else None
      }

      # Submit ticket
      result = anvil.server.call('create_ticket', customer_data, ticket_data)

      if result['success']:
        ticket_number = result['ticket_number']

        Notification(f"Ticket #{ticket_number} submitted!", style="success").show()

        # Show confirmation message
        alert(
          f"Thank you! Your ticket #{ticket_number} has been submitted.\n\n"
          "We'll respond within 24 hours.",
          title="Ticket Submitted"
        )

        # Close form or redirect
        self.raise_event('x-close-alert', value=True)

      else:
        alert(f"Error: {result.get('error', 'Unknown error')}")

    except Exception as e:
      print(f"Error submitting ticket: {e}")
      alert(f"Failed to submit ticket: {str(e)}")

  @handle("file_attachments", "change")
  def file_attachments_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    pass

  @handle("btn_submit", "click")
  def btn_submit_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
