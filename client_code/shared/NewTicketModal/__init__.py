from ._anvil_designer import NewTicketModalTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class NewTicketModal(NewTicketModalTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)

    # Configure fields
    self.txt_subject.placeholder = "Brief description of your issue"

    self.dd_category.items = [
      ('General', 'general'),
      ('Billing', 'billing'),
      ('Technical', 'technical'),
      ('Complaint', 'complaint')
    ]
    self.dd_category.selected_value = 'general'

    self.dd_priority.items = [
      ('Low', 'low'),
      ('Medium', 'medium'),
      ('High', 'high'),
      ('Urgent', 'urgent')
    ]
    self.dd_priority.selected_value = 'medium'

    self.txt_description.placeholder = "Please provide details about your issue..."
    self.txt_description.rows = 8

  def save(self):
    """Submit ticket"""
    try:
      if not self.txt_subject.text:
        alert("Subject is required")
        return False

      if not self.txt_description.text or len(self.txt_description.text) < 10:
        alert("Please provide more details (at least 10 characters)")
        return False

      ticket_data = {
        'subject': self.txt_subject.text,
        'category': self.dd_category.selected_value,
        'priority': self.dd_priority.selected_value,
        'description': self.txt_description.text
      }

      result = anvil.server.call('create_ticket', ticket_data)

      if result['success']:
        Notification("Ticket created successfully!", style="success").show()
        return True
      else:
        alert(result['error'])
        return False

    except Exception as e:
      alert(f"Error creating ticket: {str(e)}")
      return False