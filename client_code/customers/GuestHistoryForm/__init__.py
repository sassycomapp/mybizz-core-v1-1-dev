from ._anvil_designer import GuestHistoryFormTemplate
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

class GuestHistoryForm(GuestHistoryFormTemplate):
  def __init__(self, guest_id=None, **properties):
    self.guest_id = guest_id
    self.guest = None
    self.init_components(**properties)

    # Configure back link
    self.link_back.text = "← Back"
    self.link_back.role = "secondary-color"

    # Configure title
    self.lbl_title.font_size = 20
    self.lbl_title.bold = True
    self.lbl_title.role = "headline"

    # Configure sections
    self.lbl_summary_section.text = "GUEST SUMMARY"
    self.lbl_summary_section.bold = True
    self.lbl_summary_section.font_size = 16

    self.lbl_bookings_section.text = "BOOKING HISTORY"
    self.lbl_bookings_section.bold = True
    self.lbl_bookings_section.font_size = 16

    self.lbl_notes_section.text = "GUEST NOTES & PREFERENCES"
    self.lbl_notes_section.bold = True
    self.lbl_notes_section.font_size = 16

    # Configure buttons
    self.btn_add_note.text = "📝 Add Note"
    self.btn_add_note.role = "secondary-color"

    self.btn_full_profile.text = "📊 View Full Profile"
    self.btn_full_profile.role = "secondary-color"

    # Set repeating panel templates
    self.rp_bookings.item_template = 'customers.GuestBookingTemplate'
    self.rp_notes.item_template = 'customers.GuestNoteTemplate'

    # Load guest history
    if self.guest_id:
      self.load_guest_history()

  def load_guest_history(self):
    """Load guest history data"""
    try:
      data = anvil.server.call('get_guest_history', self.guest_id)

      if not data:
        alert("Guest not found")
        return

      self.guest = data['guest']
      stats = data['stats']

      # Set title
      self.lbl_title.text = f"Guest History: {self.guest['email']}"

      # Display summary
      self.lbl_summary_line1.text = (
        f"Total Stays: {stats['total_stays']}  •  "
        f"Total Nights: {stats['total_nights']}  •  "
        f"Total Revenue: ${stats['total_revenue']:.2f}"
      )

      member_since = self.guest['created_at'].strftime('%b %Y') if self.guest.get('created_at') else 'Unknown'
      last_visit = stats.get('last_visit', 'Never')
      if last_visit and last_visit != 'Never':
        last_visit = last_visit.strftime('%b %Y')

      self.lbl_summary_line2.text = (
        f"Member Since: {member_since}  •  "
        f"Last Visit: {last_visit}"
      )

      avg_stay = stats['total_nights'] / stats['total_stays'] if stats['total_stays'] > 0 else 0
      favorite_room = stats.get('favorite_room', 'None')

      self.lbl_summary_line3.text = (
        f"Average Stay: {avg_stay:.1f} nights  •  "
        f"Favorite Room: {favorite_room}"
      )

      # Display bookings
      self.rp_bookings.items = data['bookings']

      # Display notes
      self.rp_notes.items = data['notes']

    except Exception as e:
      alert(f"Error loading guest history: {str(e)}")

  def button_add_note_click(self, **event_args):
    """Add new note"""
    note_text = alert(
      content=TextArea(placeholder="Enter note..."),
      title="Add Guest Note",
      buttons=[("Cancel", False), ("Save", True)]
    )

    if note_text and note_text.text:
      try:
        anvil.server.call('add_guest_note', self.guest_id, note_text.text)
        Notification("Note added", style="success").show()
        self.load_guest_history()
      except Exception as e:
        alert(f"Error: {str(e)}")

  def button_full_profile_click(self, **event_args):
    """View full customer profile"""
    open_form('customers.CustomerDetailForm', customer_id=self.guest_id)

  @handle("link_back", "click")
  def link_back_click(self, **event_args):
    """Go back"""
    open_form('customers.CustomerListForm')

  @handle("btn_add_note", "click")
  def btn_add_note_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_full_profile", "click")
  def btn_full_profile_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
