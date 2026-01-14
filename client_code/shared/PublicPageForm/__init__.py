from ._anvil_designer import PublicPageFormTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class PublicPageForm(PublicPageFormTemplate):
  """Public page display with dynamic component rendering"""

  def __init__(self, slug=None, **properties):
    self.slug = slug
    self.init_components(**properties)

    # Load page
    if slug:
      self.load_page()
    else:
      alert("No page specified")

  def load_page(self):
    """Load and render page"""
    try:
      result = anvil.server.call('get_page_by_slug', self.slug)

      if result['success']:
        page = result['data']
        components = page.get('components', [])

        # Clear container
        self.col_content.clear()

        # Render each component
        for component in components:
          rendered = self.render_component(component)
          if rendered:
            self.col_content.add_component(rendered)

      else:
        alert("Page not found")
        open_form('shared.KnowledgeBaseForm')  # Redirect to help

    except Exception as e:
      print(f"Error loading page: {e}")
      alert(f"Failed to load page: {str(e)}")
      open_form('shared.KnowledgeBaseForm')

  def render_component(self, component):
    """
    Render component based on type.
    
    Args:
      component (dict): Component data with 'type' and 'data' keys
      
    Returns:
      Component: Rendered Anvil component or None
    """
    comp_type = component.get('type')
    data = component.get('data', {})

    if comp_type == 'hero':
      return self.render_hero(data)
    elif comp_type == 'text':
      return self.render_text_block(data)
    elif comp_type == 'image':
      return self.render_image(data)
    elif comp_type == 'gallery':
      return self.render_gallery(data)
    elif comp_type == 'cta':
      return self.render_cta_button(data)
    else:
      print(f"Unknown component type: {comp_type}")
      return None

  def render_hero(self, data):
    """Render hero section"""
    col = ColumnPanel(spacing='medium', background='#F5F5F5')
    col.role = 'card'

    # Headline
    lbl_headline = Label(
      text=data.get('headline', ''),
      font_size=36,
      bold=True,
      align='center'
    )
    col.add_component(lbl_headline)

    # Subtext
    if data.get('subtext'):
      lbl_subtext = Label(
        text=data['subtext'],
        font_size=18,
        align='center',
        foreground='#666666'
      )
      col.add_component(lbl_subtext)

    # CTA button
    if data.get('cta_text'):
      btn_cta = Button(
        text=data['cta_text'],
        role='primary-color',
        url=data.get('cta_url', '#')
      )
      col.add_component(btn_cta)

    return col

  def render_text_block(self, data):
    """Render text block"""
    col = ColumnPanel(spacing='small')

    # Heading
    if data.get('heading'):
      lbl_heading = Label(
        text=data['heading'],
        font_size=24,
        bold=True
      )
      col.add_component(lbl_heading)

    # Content
    if data.get('content'):
      lbl_content = Label(
        text=data['content'],
        font_size=14
      )
      col.add_component(lbl_content)

    return col

  def render_image(self, data):
    """Render image"""
    col = ColumnPanel(spacing='small', align='center')

    # Image
    if data.get('image'):
      img = Image(
        source=data['image'],
        height=400
      )
      col.add_component(img)

    # Caption
    if data.get('caption'):
      lbl_caption = Label(
        text=data['caption'],
        foreground='#666666',
        italic=True,
        align='center',
        font_size=12
      )
      col.add_component(lbl_caption)

    return col

  def render_gallery(self, data):
    """Render image gallery"""
    flow = FlowPanel(spacing='medium')

    images = data.get('images', [])

    if not images:
      return Label(text="No images in gallery", foreground='#999999')

    for img_data in images:
      img = Image(
        source=img_data,
        height=200,
        spacing_above='small',
        spacing_below='small'
      )
      flow.add_component(img)

    return flow

  def render_cta_button(self, data):
    """Render CTA button"""
    col = ColumnPanel(align='center')

    btn = Button(
      text=data.get('text', 'Click Here'),
      role='primary-color',
      url=data.get('url', '#'),
      icon='fa:arrow-right'
    )

    col.add_component(btn)

    return col