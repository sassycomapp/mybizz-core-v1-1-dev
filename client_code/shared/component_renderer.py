import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import *

"""
Component Renderer
Dynamically render Anvil components from JSON definitions
Used by page editor and public page views
"""


def render_component(component_data):
  """
  Render a component from JSON data.
  
  Args:
    component_data (dict): Component definition
      {
        'type': str,      # Component type
        'data': dict      # Component-specific data
      }
    
  Returns:
    Component: Anvil component (Label, Image, Button, etc.)
    
  Example:
    >>> component_data = {
    >>>   'type': 'hero',
    >>>   'data': {
    >>>     'headline': 'Welcome',
    >>>     'subheadline': 'Great services',
    >>>     'image_url': 'https://...',
    >>>     'cta_text': 'Book Now',
    >>>     'cta_link': '/book'
    >>>   }
    >>> }
    >>> component = render_component(component_data)
  """
  if not component_data:
    return Label(text="[Empty Component]", foreground="#999999")

  component_type = component_data.get('type')
  data = component_data.get('data', {})

  # Route to appropriate renderer
  renderers = {
    'hero': render_hero,
    'text_block': render_text_block,
    'image': render_image,
    'image_gallery': render_image_gallery,
    'cta_button': render_cta_button,
    'contact_form': render_contact_form,
    'video_embed': render_video_embed,
    'spacer': render_spacer,
    'divider': render_divider,
    'card': render_card,
    'feature_list': render_feature_list
  }

  renderer = renderers.get(component_type)

  if renderer:
    try:
      return renderer(data)
    except Exception as e:
      return Label(
        text=f"[Error rendering {component_type}: {str(e)}]",
        foreground="red"
      )
  else:
    return Label(
      text=f"[Unknown component type: {component_type}]",
      foreground="orange"
    )

def render_hero(data):
  """
  Render hero section component.
  
  Data format:
    {
      'headline': str,
      'subheadline': str,
      'image_url': str,
      'cta_text': str,
      'cta_link': str,
      'alignment': str ('left', 'center', 'right')
    }
  """
  container = ColumnPanel(
    spacing='medium',
    spacing_above='large',
    spacing_below='large'
  )

  # Background image if provided
  if data.get('image_url'):
    container.background = data['image_url']

  # Headline
  if data.get('headline'):
    headline = Label(
      text=data['headline'],
      font_size=32,
      bold=True,
      align=data.get('alignment', 'center')
    )
    container.add_component(headline)

  # Subheadline
  if data.get('subheadline'):
    subheadline = Label(
      text=data['subheadline'],
      font_size=18,
      align=data.get('alignment', 'center'),
      foreground="#666666"
    )
    container.add_component(subheadline)

  # CTA Button
  if data.get('cta_text') and data.get('cta_link'):
    cta = Button(
      text=data['cta_text'],
      role='primary-color',
      spacing_above='medium'
    )
    cta.tag = {'link': data['cta_link']}
    cta.set_event_handler('click', lambda **e: open_form_by_link(e['sender'].tag['link']))
    container.add_component(cta)

  return container

def render_text_block(data):
  """
  Render text block component.
  
  Data format:
    {
      'heading': str,
      'body': str,
      'alignment': str ('left', 'center', 'right')
    }
  """
  container = ColumnPanel(
    spacing='small',
    spacing_above='medium',
    spacing_below='medium'
  )

  # Heading
  if data.get('heading'):
    heading = Label(
      text=data['heading'],
      font_size=24,
      bold=True,
      align=data.get('alignment', 'left')
    )
    container.add_component(heading)

  # Body text
  if data.get('body'):
    body = Label(
      text=data['body'],
      align=data.get('alignment', 'left')
    )
    container.add_component(body)

  return container

def render_image(data):
  """
  Render single image component.
  
  Data format:
    {
      'image_url': str,
      'caption': str,
      'alt_text': str,
      'width': int (optional),
      'height': int (optional),
      'alignment': str
    }
  """
  container = ColumnPanel(spacing='small')

  if data.get('image_url'):
    img = Image(
      source=data['image_url'],
      spacing_above='medium',
      spacing_below='small'
    )

    if data.get('height'):
      img.height = data['height']

    container.add_component(img)

  # Caption
  if data.get('caption'):
    caption = Label(
      text=data['caption'],
      italic=True,
      foreground="#666666",
      align=data.get('alignment', 'center')
    )
    container.add_component(caption)

  return container

def render_image_gallery(data):
  """
  Render image gallery component.
  
  Data format:
    {
      'images': [str],  # List of image URLs
      'layout': str ('grid', 'slider'),
      'columns': int (for grid layout)
    }
  """
  images = data.get('images', [])
  layout = data.get('layout', 'grid')

  if layout == 'grid':
    container = FlowPanel(spacing='small', spacing_above='medium')

    for img_url in images:
      img = Image(
        source=img_url,
        height=200,
        spacing='small'
      )
      container.add_component(img)
  else:
    # Slider layout (simplified)
    container = ColumnPanel(spacing='small', spacing_above='medium')

    if images:
      # Show first image (in real implementation, would have prev/next buttons)
      img = Image(
        source=images[0],
        height=400
      )
      container.add_component(img)

      # Navigation hint
      nav = Label(
        text=f"Image 1 of {len(images)}",
        align='center',
        foreground="#666666"
      )
      container.add_component(nav)

  return container

def render_cta_button(data):
  """
  Render call-to-action button.
  
  Data format:
    {
      'text': str,
      'link': str,
      'style': str ('primary', 'secondary', 'outlined'),
      'alignment': str
    }
  """
  container = ColumnPanel(spacing_above='medium', spacing_below='medium')

  btn = Button(
    text=data.get('text', 'Click Here'),
    role=f"{data.get('style', 'primary')}-color"
  )

  btn.tag = {'link': data.get('link', '/')}
  btn.set_event_handler('click', lambda **e: open_form_by_link(e['sender'].tag['link']))

  # Alignment
  if data.get('alignment') == 'center':
    flow = FlowPanel(align='center')
    flow.add_component(btn)
    container.add_component(flow)
  else:
    container.add_component(btn)

  return container

def render_contact_form(data):
  """
  Render contact form component.
  
  Data format:
    {
      'heading': str,
      'submit_text': str,
      'fields': list ['name', 'email', 'phone', 'message']
    }
  """
  container = ColumnPanel(
    spacing='small',
    spacing_above='large',
    spacing_below='large'
  )

  # Heading
  if data.get('heading'):
    heading = Label(
      text=data['heading'],
      font_size=20,
      bold=True
    )
    container.add_component(heading)

  # Fields
  fields = data.get('fields', ['name', 'email', 'message'])

  if 'name' in fields:
    container.add_component(TextBox(placeholder="Your Name"))

  if 'email' in fields:
    container.add_component(TextBox(placeholder="Your Email", type="email"))

  if 'phone' in fields:
    container.add_component(TextBox(placeholder="Phone Number", type="tel"))

  if 'message' in fields:
    container.add_component(TextArea(placeholder="Your Message", rows=5))

  # Submit button
  submit_btn = Button(
    text=data.get('submit_text', 'Send Message'),
    role='primary-color'
  )
  container.add_component(submit_btn)

  return container

def render_video_embed(data):
  """
  Render video embed component.
  
  Data format:
    {
      'video_url': str,  # YouTube or Vimeo URL
      'title': str
    }
  """
  container = ColumnPanel(spacing='small', spacing_above='medium')

  if data.get('title'):
    title = Label(
      text=data['title'],
      font_size=18,
      bold=True
    )
    container.add_component(title)

  # Video placeholder (in real implementation, would embed iframe)
  video_url = data.get('video_url', '')

  video_placeholder = Label(
    text=f"🎥 Video: {video_url}",
    background="#000000",
    foreground="#FFFFFF",
    align='center',
    spacing_above='small'
  )
  container.add_component(video_placeholder)

  return container

def render_spacer(data):
  """
  Render spacer component.
  
  Data format:
    {
      'height': int  # Height in pixels
    }
  """
  height = data.get('height', 50)

  return Label(text="", height=height)

def render_divider(data):
  """
  Render horizontal divider.
  
  Data format:
    {
      'style': str ('solid', 'dashed', 'dotted'),
      'color': str
    }
  """
  divider = Label(
    text="─" * 50,
    foreground=data.get('color', '#CCCCCC'),
    align='center',
    spacing_above='medium',
    spacing_below='medium'
  )

  return divider

def render_card(data):
  """
  Render card component.
  
  Data format:
    {
      'image_url': str,
      'title': str,
      'description': str,
      'link': str,
      'link_text': str
    }
  """
  container = ColumnPanel(
    spacing='small',
    background='#FFFFFF',
    border='1px solid #E0E0E0',
    spacing_above='medium'
  )

  # Image
  if data.get('image_url'):
    img = Image(source=data['image_url'], height=200)
    container.add_component(img)

  # Content area
  content = ColumnPanel(spacing='small')

  # Title
  if data.get('title'):
    title = Label(
      text=data['title'],
      font_size=18,
      bold=True
    )
    content.add_component(title)
  
  # Description
  if data.get('description'):
    desc = Label(text=data['description'])
    content.add_component(desc)
  
  # Link
  if data.get('link') and data.get('link_text'):
    link = Link(
      text=data['link_text'],
      role='secondary-color'
    )
    link.tag = {'link': data['link']}
    link.set_event_handler('click', lambda **e: open_form_by_link(e['sender'].tag['link']))
    content.add_component(link)
  
  container.add_component(content)
  
  return container

def render_feature_list(data):
  """
  Render feature list component.
  
  Data format:
    {
      'heading': str,
      'features': [
        {'icon': str, 'title': str, 'description': str}
      ]
    }
  """
  container = ColumnPanel(spacing='medium', spacing_above='large')
  
  # Heading
  if data.get('heading'):
    heading = Label(
      text=data['heading'],
      font_size=24,
      bold=True
    )
    container.add_component(heading)
  
  # Features
  features = data.get('features', [])
  
  for feature in features:
    feature_panel = FlowPanel(spacing='small', spacing_above='small')
    
    # Icon
    if feature.get('icon'):
      icon = Label(
        text=feature['icon'],
        font_size=24
      )
      feature_panel.add_component(icon)
    
    # Content
    content = ColumnPanel(spacing='small')
    
    if feature.get('title'):
      title = Label(
        text=feature['title'],
        bold=True
      )
      content.add_component(title)
    
    if feature.get('description'):
      desc = Label(
        text=feature['description'],
        foreground='#666666'
      )
      content.add_component(desc)
    
    feature_panel.add_component(content)
    container.add_component(feature_panel)
  
  return container

def open_form_by_link(link):
  """
  Open form based on link path.
  
  Args:
    link (str): Link path
  """
  if not link:
    return
  
  # Parse link
  if link.startswith('/'):
    link = link[1:]
  
  # Route to appropriate form
  if link == 'book' or link == 'booking':
    open_form('booking.PublicBookingForm')
  elif link == 'shop':
    open_form('products.PublicCatalogForm')
  elif link == 'blog':
    open_form('blog.BlogListForm')
  elif link == 'contact':
    open_form('shared.ContactForm')
  else:
    # Generic page
    alert(f"Navigate to: {link}")

def render_page_components(components):
  """
  Render a list of components.
  
  Args:
    components (list): List of component definitions
    
  Returns:
    list: List of rendered Anvil components
    
  Example:
    >>> components = [
    >>>   {'type': 'hero', 'data': {...}},
    >>>   {'type': 'text_block', 'data': {...}}
    >>> ]
    >>> rendered = render_page_components(components)
  """
  rendered = []
  
  for component_data in components:
    component = render_component(component_data)
    if component:
      rendered.append(component)
  
  return rendered

# Export all functions
__all__ = [
  'render_component',
  'render_page_components',
  'render_hero',
  'render_text_block',
  'render_image',
  'render_image_gallery',
  'render_cta_button',
  'render_contact_form',
  'render_video_embed',
  'render_spacer',
  'render_divider',
  'render_card',
  'render_feature_list'
]
```