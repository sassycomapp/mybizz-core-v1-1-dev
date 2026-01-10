from ._anvil_designer import frm_doc_displayTemplate
from anvil import *
import anvil.server

class frm_doc_display(frm_doc_displayTemplate):
  def __init__(self, **properties):
    self.init_components(**properties)
    self.current_file = None
    self.original_markdown = None
    self.load_doc_list()

  def load_doc_list(self):
    """Populate dropdown with available docs"""
    docs = anvil.server.call('list_markdown_docs')
    self.dd_select_doc.items = docs

  @handle("btn_select_doc", "click")
  def btn_select_doc_click(self, **event_args):
    """Load and display selected document"""
    if not self.dd_select_doc.selected_value:
      Notification("Please select a document", style="warning").show()
      return

    self.current_file = self.dd_select_doc.selected_value
    result = anvil.server.call('load_markdown_doc', self.current_file)

    if result['success']:
      self.rt_doc_display.content = result['html']
      self.rt_doc_display.format = 'restricted_html'
      self.original_markdown = result['markdown']
      # Show view mode
      self.rt_doc_display.visible = True
      self.txt_edit_doc.visible = False
      self.btn_edit.visible = True
      self.btn_save.visible = False
      self.btn_cancel.visible = False
    else:
      Notification(f"Error loading doc: {result['error']}", style="danger").show()

  @handle("btn_edit", "click")
  def btn_edit_click(self, **event_args):
    """Switch to edit mode"""
    self.txt_edit_doc.text = self.original_markdown
    self.rt_doc_display.visible = False
    self.txt_edit_doc.visible = True
    self.btn_edit.visible = False
    self.btn_save.visible = True
    self.btn_cancel.visible = True

  @handle("btn_save", "click")
  def btn_save_click(self, **event_args):
    """Save edited markdown"""
    result = anvil.server.call('save_markdown_doc', 
                               self.current_file, 
                               self.txt_edit_doc.text)

    if result['success']:
      Notification("Document saved successfully", style="success").show()
      # Reload to show updated HTML
      self.btn_select_doc_click()
    else:
      Notification(f"Error saving: {result['error']}", style="danger").show()

  @handle("btn_cancel", "click")
  def btn_cancel_click(self, **event_args):
    """Cancel editing and return to view mode"""
    self.btn_select_doc_click()

  @handle("btn_save_new", "click")
  def btn_save_new_click(self, **event_args):
    """Upload new markdown file"""
    if not self.fl_new_doc.file:
      Notification("Please select a file first", style="warning").show()
      return

    file = self.fl_new_doc.file
    filename = file.name

    # Upload the file
    result = anvil.server.call('upload_new_doc', file, filename)

    if result['success']:
      Notification(result['message'], style="success").show()
      # Refresh the dropdown list
      self.load_doc_list()
      # Clear the file loader and label
      self.fl_new_doc.clear()
      self.lbl_new_file_name.text = ""
      self.lbl_new_file_name.visible = False
    else:
      Notification(f"Error: {result['error']}", style="danger").show()

  @handle("fl_new_doc", "change")
  def fl_new_doc_change(self, file, **event_args):
    """Display selected filename when file is chosen"""
    if file:
      self.lbl_new_file_name.text = f"Selected: {file.name}"
      self.lbl_new_file_name.visible = True
    else:
      self.lbl_new_file_name.text = ""
      self.lbl_new_file_name.visible = False