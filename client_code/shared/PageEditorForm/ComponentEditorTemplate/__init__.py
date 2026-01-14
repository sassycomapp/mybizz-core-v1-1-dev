from ._anvil_designer import ComponentEditorTemplateTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ComponentEditorTemplate(ComponentEditorTemplateTemplate):
  """Component editor row"""

  def __init__(self, **properties):
    self.component_data = self.item
    self.init_components(**properties)

    index = self.component_data['index']
    component = self.component_data['component']

    # Component type label
    type_names = {
      'hero': 'Hero Section',
      'text': 'Text Block',
      'image': 'Image',
      'gallery': 'Image Gallery',
      'cta': 'CTA Button'
    }

    self.lbl_type.text = type_names.get(component['type'], component['type'])
    self.lbl_type.font_size = 14
    self.lbl_type.bold = True

    # Configure buttons
    self.btn_edit.text = "Edit"
    self.btn_edit.role = "outlined-button"

    self.btn_delete.text = "Delete"
    self.btn_delete.role = "outlined-button"

    self.btn_move_up.text = "↑"
    self.btn_move_up.enabled = (index > 0)

    self.btn_move_down.text = "↓"
    # Note: We can't check if it's last without knowing total count
    # Parent form will handle this

  def button_edit_click(self, **event_args):
    """Edit component"""
    index = self.component_data['index']
    self.parent.raise_event('x-component-edit', index=index)

  def button_delete_click(self, **event_args):
    """Delete component"""
    index = self.component_data['index']
    self.parent.raise_event('x-component-delete', index=index)

  def button_move_up_click(self, **event_args):
    """Move component up"""
    index = self.component_data['index']
    self.parent.raise_event('x-component-move-up', index=index)

  def button_move_down_click(self, **event_args):
    """Move component down"""
    index = self.component_data['index']
    self.parent.raise_event('x-component-move-down', index=index)