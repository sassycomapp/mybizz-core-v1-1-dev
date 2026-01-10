import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.stripe
import anvil.secrets
import anvil.files
from anvil.files import data_files
import anvil.email
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import markdown

@anvil.server.callable
def list_markdown_docs():
  """Returns display names with hierarchy, actual paths as values"""
  docs = []
  for row in app_tables.files.search():
    path = row['path']
    if path and path.endswith('.md'):
      # Convert path to visual hierarchy
      display = path.replace('/', ' → ')
      docs.append(display)  # Just the display string
  return sorted(docs)


@anvil.server.callable
def load_markdown_doc(filename):
  """Load and convert markdown to HTML"""
  try:
    # Find the file in Files table
    row = app_tables.files.get(path=filename)

    if not row:
      return {'success': False, 'error': f'File not found: {filename}'}

    # Get the media object
    media = row['file']

    # Read markdown content
    md_text = media.get_bytes().decode('utf-8')

    # Convert to HTML with extensions
    html = markdown.markdown(md_text, extensions=['extra', 'codehilite', 'fenced_code'])

    return {
      'success': True, 
      'html': html, 
      'markdown': md_text,
      'filename': filename
    }
  except Exception as e:
    return {'success': False, 'error': str(e)}

@anvil.server.callable
def save_markdown_doc(filename, markdown_text):
  """Save edited markdown back to Files table"""
  try:
    # Find the existing row
    row = app_tables.files.get(path=filename)

    if not row:
      return {'success': False, 'error': f'File not found: {filename}'}

    # Create new media object with updated content
    from anvil import BlobMedia
    new_media = BlobMedia(
      content_type='text/markdown',
      content=markdown_text.encode('utf-8'),
      name=filename
    )

    # Update the row
    row['file'] = new_media

    return {'success': True, 'message': 'Document saved successfully'}
  except Exception as e:
    return {'success': False, 'error': str(e)}

@anvil.server.callable
def upload_new_doc(file, filename):
  """Upload a new markdown file to Files table"""
  try:
    # Validate it's a .md file
    if not filename.endswith('.md'):
      return {'success': False, 'error': 'Only .md files are allowed'}

    # Check if file already exists
    existing = app_tables.files.get(path=filename)

    if existing:
      # Update existing file
      existing['file'] = file
      message = f'{filename} updated successfully'
    else:
      # Create new row
      app_tables.files.add_row(
        path=filename,
        file=file,
        file_version='1.0'
      )
      message = f'{filename} uploaded successfully'

    return {'success': True, 'message': message}
  except Exception as e:
    return {'success': False, 'error': str(e)}


@anvil.server.callable
def delete_markdown_doc(filename):
  row = app_tables.files.get(path=filename)
  if row:
    row.delete()
    return {'success': True}
  return {'success': False, 'error': 'File not found'}
