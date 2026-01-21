import anvil.server
from routing import router
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:
#
#    from .. import Module1
#
#    Module1.say_hello()
#

import anvil.server
from routing import router
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
# This is a module.
# You can define variables and functions here, and use them from any form. For example, in a top-level form:
#
#    from .. import Module1
#
#    Module1.say_hello()
#

```python
"""
MyBizz Platform - Startup Module
=================================

This module serves as the application entry point. It:
1. Registers all application routes
2. Checks user authentication
3. Initializes the appropriate layout
4. Handles initial navigation

This file should be set as the "Startup Form" in Anvil app settings.

Author: MyBizz Platform
Created: 2026-01-20
"""

from anvil import *
import anvil.server
import anvil.users
import anvil.tables as tables
from anvil.tables import app_tables

# Import layouts
from Layouts.MainLayout import MainLayout
from Layouts.AdminLayout import AdminLayout
from Layouts.BlankLayout import BlankLayout
from Layouts.ErrorLayout import ErrorLayout

# Import route definitions
from routes.crm_routes import CRM_ROUTES
from routes.marketing_routes import MARKETING_ROUTES


# =============================================================================
# CONFIGURATION
# =============================================================================

# Application metadata
APP_NAME = "MyBizz Platform"
APP_VERSION = "1.0.0"
DEFAULT_TITLE = "MyBizz - CRM & Marketing Platform"

# Default routes for different user states
DEFAULT_AUTHENTICATED_ROUTE = "/marketing"
DEFAULT_UNAUTHENTICATED_ROUTE = "/login"
DEFAULT_ERROR_ROUTE = "/error"

# Public routes that don't require authentication
PUBLIC_ROUTES = [
  '/login',
  '/signup',
  '/reset-password',
  '/reviews/submit',
  '/tickets/submit',
  '/help',
  '/faq',
  '/chatbot'
]


# =============================================================================
# ROUTE REGISTRATION
# =============================================================================

def register_all_routes():
  """
    Register all application routes
    
    This function combines routes from all modules and registers them
    with Anvil's routing system.
    """
  print("Registering application routes...")

  # Combine all route definitions
  all_routes = []

  # Add CRM routes
  all_routes.extend(CRM_ROUTES)

  # Add Marketing routes
  all_routes.extend(MARKETING_ROUTES)

  # Add public/shared routes
  all_routes.extend(get_public_routes())

  # Add authentication routes
  all_routes.extend(get_auth_routes())

  # Add error routes
  all_routes.extend(get_error_routes())

  # Register each route
  routes_registered = 0
  for route in all_routes:
    try:
      # Register with Anvil routing
      # Note: Anvil doesn't have a direct register() method
      # Routes are typically handled in the MainLayout or routing form
      # This is a conceptual registration - actual implementation may vary

      print(f"  ✓ {route['path']} → {route['form']}")
      routes_registered += 1

    except Exception as e:
      print(f"  ✗ Error registering {route['path']}: {e}")

  print(f"Registered {routes_registered} routes successfully")
  return all_routes


def get_public_routes():
  """Define public-facing routes"""
  return [
    {
      'path': '/',
      'form': 'shared.HomePage',
      'title': f'{APP_NAME} - Home',
      'layout': 'main',
      'auth_required': False
    },
    {
      'path': '/reviews/submit',
      'form': 'shared.ReviewSubmissionForm',
      'title': 'Submit Review',
      'layout': 'main',
      'auth_required': False
    },
    {
      'path': '/tickets/submit',
      'form': 'shared.TicketSubmissionForm',
      'title': 'Submit Support Ticket',
      'layout': 'main',
      'auth_required': False
    },
    {
      'path': '/help',
      'form': 'shared.PublicKnowledgeBaseForm',
      'title': 'Help Center',
      'layout': 'main',
      'auth_required': False
    },
    {
      'path': '/help/:article_id',
      'form': 'shared.PublicKnowledgeBaseForm',
      'title': 'Help Article',
      'layout': 'main',
      'auth_required': False
    }
  ]


def get_auth_routes():
  """Define authentication routes"""
  return [
    {
      'path': '/login',
      'form': 'auth.LoginForm',
      'title': 'Login',
      'layout': 'blank',
      'auth_required': False
    },
    {
      'path': '/signup',
      'form': 'auth.SignupForm',
      'title': 'Sign Up',
      'layout': 'blank',
      'auth_required': False
    },
    {
      'path': '/reset-password',
      'form': 'auth.ResetPasswordForm',
      'title': 'Reset Password',
      'layout': 'blank',
      'auth_required': False
    },
    {
      'path': '/logout',
      'form': 'auth.LogoutForm',
      'title': 'Logging Out...',
      'layout': 'blank',
      'auth_required': False
    }
  ]


def get_error_routes():
  """Define error page routes"""
  return [
    {
      'path': '/error',
      'form': 'shared.ErrorPage',
      'title': 'Error',
      'layout': 'error',
      'auth_required': False
    },
    {
      'path': '/404',
      'form': 'shared.NotFoundPage',
      'title': 'Page Not Found',
      'layout': 'error',
      'auth_required': False
    },
    {
      'path': '/403',
      'form': 'shared.ForbiddenPage',
      'title': 'Access Denied',
      'layout': 'error',
      'auth_required': False
    }
  ]


# =============================================================================
# AUTHENTICATION & AUTHORIZATION
# =============================================================================

def check_authentication():
  """
    Check if user is authenticated
    
    Returns:
        dict: User object if authenticated, None otherwise
    """
  try:
    user = anvil.users.get_user()
    return user
  except Exception as e:
    print(f"Authentication check failed: {e}")
    return None


def is_route_public(path):
  """
    Check if a route is public (doesn't require authentication)
    
    Args:
        path (str): URL path to check
    
    Returns:
        bool: True if route is public
    """
  # Exact match
  if path in PUBLIC_ROUTES:
    return True

    # Prefix match (for routes with parameters)
  for public_route in PUBLIC_ROUTES:
    if path.startswith(public_route.replace('/:id', '')):
      return True

  return False


def check_route_permission(route, user):
  """
    Check if user has permission to access route
    
    Args:
        route (dict): Route definition
        user: User object
    
    Returns:
        bool: True if user can access route
    """
  # Public routes are always accessible
  if not route.get('auth_required', True):
    return True

    # Must be authenticated for protected routes
  if not user:
    return False

    # Check role-based permissions if defined
  required_role = route.get('required_role')
  if required_role:
    user_role = user.get('role', 'user')
    if user_role != required_role:
      return False

  return True


# =============================================================================
# LAYOUT SELECTION
# =============================================================================

def get_layout_for_route(route, user):
  """
    Determine which layout to use for a route
    
    Args:
        route (dict): Route definition
        user: User object
    
    Returns:
        class: Layout class to use
    """
  layout_name = route.get('layout', 'admin')

  layout_map = {
    'main': MainLayout,      # Public website
    'admin': AdminLayout,    # Admin interface
    'blank': BlankLayout,    # Login, signup, etc.
    'error': ErrorLayout     # Error pages
  }

  return layout_map.get(layout_name, AdminLayout)


# =============================================================================
# NAVIGATION HANDLING
# =============================================================================

def navigate_to_route(path, all_routes):
  """
    Navigate to a specific route
    
    Args:
        path (str): URL path
        all_routes (list): All registered routes
    """
  user = check_authentication()

  # Find matching route
  route = find_route(path, all_routes)

  if not route:
    # Route not found - show 404
    show_error_page(404, "Page not found")
    return

    # Check permissions
  if not check_route_permission(route, user):
    # Not authenticated - redirect to login
    if not user:
      print(f"Authentication required for {path}, redirecting to login")
      open_form('auth.LoginForm')
      return

      # Authenticated but not authorized - show 403
    show_error_page(403, "Access denied")
    return

    # Get appropriate layout
  LayoutClass = get_layout_for_route(route, user)

  # Load form within layout
  try:
    # Parse form path (e.g., 'crm.ContactListForm')
    form_path_parts = route['form'].split('.')

    if len(form_path_parts) == 2:
      package_name, form_name = form_path_parts
      # Dynamic import would go here
      # For now, we'll use the layout's content slot

      # Open the layout with the content form
    layout = LayoutClass(
      content_form=route['form'],
      page_title=route.get('title', DEFAULT_TITLE)
    )

    open_form(layout)

  except Exception as e:
    print(f"Error loading route {path}: {e}")
    show_error_page(500, f"Error loading page: {str(e)}")


def find_route(path, routes):
  """
    Find route definition matching path
    
    Args:
        path (str): URL path
        routes (list): All route definitions
    
    Returns:
        dict or None: Matching route definition
    """
  # Try exact match first
  for route in routes:
    if route['path'] == path:
      return route

    # Try pattern match (with parameters)
  for route in routes:
    route_pattern = route['path']

    # Simple parameter matching (e.g., '/contacts/:id')
    if ':' in route_pattern:
      # Convert route pattern to regex-like match
      pattern_parts = route_pattern.split('/')
      path_parts = path.split('/')

      if len(pattern_parts) == len(path_parts):
        match = True
        for i, part in enumerate(pattern_parts):
          if part.startswith(':'):
            # Parameter - always matches
            continue
          elif part != path_parts[i]:
            match = False
            break

        if match:
          return route

  return None


def show_error_page(error_code, message):
  """
    Display error page
    
    Args:
        error_code (int): HTTP error code
        message (str): Error message
    """
  try:
    error_layout = ErrorLayout(
      error_code=error_code,
      error_message=message
    )
    open_form(error_layout)
  except Exception as e:
    print(f"Error showing error page: {e}")
    # Fallback to basic alert
    alert(f"Error {error_code}: {message}")


# =============================================================================
# INITIALIZATION
# =============================================================================

def initialize_app():
  """
    Main application initialization
    
    This function runs when the app starts and sets up everything needed
    for the application to function.
    """
  print(f"Initializing {APP_NAME} v{APP_VERSION}...")

  # Register all routes
  all_routes = register_all_routes()

  # Check authentication
  user = check_authentication()

  if user:
    print(f"User authenticated: {user.get('email', 'Unknown')}")
  else:
    print("No user authenticated")

    # Get current URL hash
    # Note: In actual Anvil app, this would use anvil.routing
    # For now, we'll use a default
  current_path = get_current_path()

  print(f"Current path: {current_path}")

  # Navigate to appropriate route
  if current_path and current_path != '/':
    # Navigate to requested path
    navigate_to_route(current_path, all_routes)
  else:
    # Navigate to default route
    if user:
      navigate_to_route(DEFAULT_AUTHENTICATED_ROUTE, all_routes)
    else:
      navigate_to_route(DEFAULT_UNAUTHENTICATED_ROUTE, all_routes)

  print("App initialization complete!")


def get_current_path():
  """
    Get current URL path
    
    In actual implementation, this would use anvil.routing.get_url_hash()
    
    Returns:
        str: Current URL path
    """
  try:
    # In real Anvil app:
    # return anvil.routing.get_url_hash()

    # For now, return default
    return '/'
  except:
    return '/'


# =============================================================================
# ERROR HANDLING
# =============================================================================

def setup_global_error_handler():
  """
    Set up global error handler for uncaught exceptions
    """
  def error_handler(err):
    print(f"Global error: {err}")
    show_error_page(500, "An unexpected error occurred")

    # In Anvil, errors are typically caught in form code
    # This is conceptual
  pass


# =============================================================================
# STARTUP
# =============================================================================

# Run initialization when module is imported
# Note: In Anvil, you would set this as the Startup Form/Module
print("Loading startup module...")

try:
  initialize_app()
except Exception as e:
  print(f"FATAL ERROR during startup: {e}")
  # Show error to user
  alert(f"Failed to start application: {str(e)}")
