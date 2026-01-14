from ._anvil_designer import PageEditorFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class PageEditorForm(PageEditorFormTemplate):
  """Component-based page editor"""

  def __init__(self, **properties):
    self.components = []
    self.current_page = None
    self.init_components(**properties)

    # Check permissions
    user = anvil.users.get_user()
    if not user or user['role'] not in ['owner', 'manager']:
      alert("Access denied")
      open_form('dashboard.DashboardForm')
      return

    # Configure title
    self.lbl_title.text = "Page Editor"
    self.lbl_title.font_size = 24
    self.lbl_title.bold = True

    # Configure labels
    self.lbl_components.text = "Page Components:"
    self.lbl_components.font_size = 18
    self.lbl_components.bold = True

    # Configure buttons
    self.btn_new_page.text = "New Page"
    self.btn_new_page.icon = "fa:plus"

    self.btn_add_component.text = "Add Component"
    self.btn_add_component.icon = "fa:plus"
    self.btn_add_component.role = "primary-color"

    self.btn_save_draft.text = "Save Draft"
    self.btn_save_draft.role = "outlined-button"

    self.btn_publish.text = "Publish"
    self.btn_publish.role = "primary-color"

    self.btn_preview.text = "Preview"
    self.btn_preview.role = "outlined-button"

    # Load pages
    self.load_pages()

  def load_pages(self):
    """Load available pages"""
    try:
      result = anvil.server.call('get_all_pages')

      if result['success']:
        pages = result['data']
        self.dd_page_selector.items = [(p['name'], p) for p in pages]

        # Select first page if available
        if pages:
          self.dd_page_selector.selected_value = pages[0]
          self.load_page_components()

      else:
        alert(f"Error loading pages: {result.get('error')}")

    except Exception as e:
      print(f"Error loading pages: {e}")
      alert(f"Failed to load pages: {str(e)}")

  def load_page_components(self):
    """Load components for selected page"""
    if not self.dd_page_selector.selected_value:
      return

    self.current_page = self.dd_page_selector.selected_value
    self.components = list(self.current_page.get('components', []))

    # Refresh display
    self.refresh_components()

  def refresh_components(self):
    """Refresh component list display"""
    self.rp_components.items = [
      {'index': i, 'component': comp} 
      for i, comp in enumerate(self.components)
    ]

  def dropdown_page_selector_change(self, **event_args):
    """Page selection changed"""
    self.load_page_components()

  def button_new_page_click(self, **event_args):
    """Create new page"""
    name = alert(
      content=TextBox(placeholder="Page name"),
      title="Create New Page",
      buttons=[("Create", True), ("Cancel", False)]
    )

    if name:
      try:
        result = anvil.server.call('create_page', name)

        if result['success']:
          Notification("Page created!", style="success").show()
          self.load_pages()
        else:
          alert(f"Error: {result.get('error')}")

      except Exception as e:
        alert(f"Failed to create page: {str(e)}")

  def button_add_component_click(self, **event_args):
    """Add component picker"""
    component_type = alert(
      content=Label(text="Select component type:"),
      title="Add Component",
      buttons=[
        ("Hero Section", 'hero'),
        ("Text Block", 'text'),
        ("Image", 'image'),
        ("Gallery", 'gallery'),
        ("CTA Button", 'cta'),
        ("Cancel", None)
      ]
    )

    if component_type:
      # Add component with default data
      new_component = {
        'type': component_type,
        'data': self.get_default_data(component_type)
      }

      self.components.append(new_component)
      self.refresh_components()

  def get_default_data(self, component_type):
    """Get default data for component type"""
    defaults = {
      'hero': {'headline': 'Welcome', 'subtext': '', 'cta_text': '', 'cta_url': ''},
      'text': {'heading': 'Heading', 'content': 'Enter content here...'},
      'image': {'image': None, 'caption': ''},
      'gallery': {'images': []},
      'cta': {'text': 'Click Here', 'url': '#'}
    }

    return defaults.get(component_type, {})

  def component_edit(self, index, **event_args):
    """Edit component (called from template)"""
    component = self.components[index]

    # Open edit dialog (simplified - you'd want a proper form)
    alert(f"Edit {component['type']} component\n(Full editor would go here)")

  def component_delete(self, index, **event_args):
    """Delete component"""
    if confirm(f"Delete this component?"):
      del self.components[index]
      self.refresh_components()

  def component_move_up(self, index, **event_args):
    """Move component up"""
    if index > 0:
      self.components[index], self.components[index-1] = \
      self.components[index-1], self.components[index]
      self.refresh_components()

  def component_move_down(self, index, **event_args):
    """Move component down"""
    if index < len(self.components) - 1:
      self.components[index], self.components[index+1] = \
      self.components[index+1], self.components[index]
      self.refresh_components()

  def button_save_draft_click(self, **event_args):
    """Save page as draft"""
    if not self.current_page:
      alert("No page selected")
      return

    try:
      result = anvil.server.call(
        'save_page', 
        self.current_page.get_id(), 
        self.components, 
        False  # Not published
      )

      if result['success']:
        Notification("Page saved as draft!", style="success").show()
      else:
        alert(f"Error: {result.get('error')}")

    except Exception as e:
      alert(f"Save failed: {str(e)}")

  def button_publish_click(self, **event_args):
    """Publish page"""
    if not self.current_page:
      alert("No page selected")
      return

    if confirm("Publish this page? It will be visible to the public."):
      try:
        result = anvil.server.call(
          'save_page', 
          self.current_page.get_id(), 
          self.components, 
          True  # Published
        )

        if result['success']:
          Notification("Page published!", style="success").show()
        else:
          alert(f"Error: {result.get('error')}")

      except Exception as e:
        alert(f"Publish failed: {str(e)}")

  def button_preview_click(self, **event_args):
    """Preview page"""
    if not self.current_page:
      alert("No page selected")
      return

    # Open preview in new window
    slug = self.current_page.get('slug', '')
    if slug:
      anvil.js.window.open(f"/page/{slug}", "_blank")
    else:
      alert("Page has no slug set")

  @handle("dd_page_selector", "change")
  def dd_page_selector_change(self, **event_args):
    """This method is called when an item is selected"""
    pass

  @handle("btn_new_page", "click")
  def btn_new_page_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_add_component", "click")
  def btn_add_component_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_preview", "click")
  def btn_preview_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_publish", "click")
  def btn_publish_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_save_draft", "click")
  def btn_save_draft_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
