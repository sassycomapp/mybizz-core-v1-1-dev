from ._anvil_designer import UsersTabTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class UsersTab(UsersTabTemplate):
  """Users & permissions management tab"""

  def __init__(self, **properties):
    self.init_components(**properties)

    self.lbl_title.text = "Users & Permissions"
    self.lbl_title.font_size = 18
    self.lbl_title.bold = True

    self.btn_invite.text = "Invite User"
    self.btn_invite.icon = "fa:user-plus"
    self.btn_invite.role = "primary-color"

    # Configure data grid
    self.dg_users.columns = [
      {'id': 'name', 'title': 'Name', 'data_key': 'name_display', 'width': 200},
      {'id': 'email', 'title': 'Email', 'data_key': 'email', 'width': 250},
      {'id': 'role', 'title': 'Role', 'data_key': 'role_display', 'width': 100},
      {'id': 'status', 'title': 'Status', 'data_key': 'status_display', 'width': 100},
      {'id': 'actions', 'title': 'Actions', 'data_key': None, 'width': 150}
    ]

    self.load_users()

  def load_users(self):
    """Load all users"""
    try:
      result = anvil.server.call('get_all_users')

      if result['success']:
        users = result['data']

        for user in users:
          # Name display
          first = user.get('first_name', '')
          last = user.get('last_name', '')
          user['name_display'] = f"{first} {last}".strip() or 'N/A'

          # Role display
          user['role_display'] = user.get('role', 'customer').title()

          # Status display
          user['status_display'] = '✅ Active' if user.get('enabled') else '⏸ Inactive'

        self.dg_users.items = users

    except Exception as e:
      alert(f"Failed to load users: {str(e)}")

  def button_invite_click(self, **event_args):
    """Invite new user"""
    email = prompt("Enter email address to invite:")

    if email:
      role = alert(
        content=Label(text="Select role for new user:"),
        title="Select Role",
        buttons=[
          ("Manager", "manager"),
          ("Staff", "staff"),
          ("Cancel", None)
        ]
      )

      if role:
        try:
          result = anvil.server.call('invite_user', email, role)

          if result['success']:
            Notification("Invitation sent!", style="success").show()
            self.load_users()
          else:
            alert(f"Error: {result.get('error')}")

        except Exception as e:
          alert(f"Failed to invite: {str(e)}")

  @handle("btn_invite", "click")
  def btn_invite_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
