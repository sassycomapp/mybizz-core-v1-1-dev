import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from anvil import *
import re

"""
Authentication UI Helper Functions
Reusable utilities for auth-related UI operations
"""


def validate_email(email):
  """
  Validate email address format.
  
  Args:
    email (str): Email to validate
    
  Returns:
    tuple: (is_valid, error_message)
    
  Example:
    >>> validate_email("user@example.com")
    (True, None)
    >>> validate_email("invalid")
    (False, "Invalid email format")
  """
  if not email:
    return (False, "Email is required")

  # Basic email regex
  pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

  if not re.match(pattern, email):
    return (False, "Invalid email format")

  return (True, None)

def validate_password(password):
  """
  Validate password strength.
  
  Args:
    password (str): Password to validate
    
  Returns:
    tuple: (is_valid, error_message, strength)
    
  Strength levels: 'weak', 'medium', 'strong'
  
  Requirements:
    - Minimum 8 characters
    - At least one letter
    - At least one number
    
  Example:
    >>> validate_password("Pass123!")
    (True, None, 'strong')
  """
  if not password:
    return (False, "Password is required", 'weak')

  if len(password) < 8:
    return (False, "Password must be at least 8 characters", 'weak')

  has_letter = bool(re.search(r'[a-zA-Z]', password))
  has_number = bool(re.search(r'\d', password))
  has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

  if not has_letter or not has_number:
    return (False, "Password must contain letters and numbers", 'weak')

  # Calculate strength
  if len(password) >= 12 and has_letter and has_number and has_special:
    strength = 'strong'
  elif len(password) >= 8 and has_letter and has_number:
    strength = 'medium'
  else:
    strength = 'weak'

  return (True, None, strength)

def check_passwords_match(password, confirm_password):
  """
  Check if passwords match.
  
  Args:
    password (str): First password
    confirm_password (str): Confirmation password
    
  Returns:
    tuple: (match, error_message)
  """
  if password != confirm_password:
    return (False, "Passwords do not match")

  return (True, None)

def format_user_display_name(user):
  """
  Format user's display name from user row.
  
  Args:
    user (dict): User row from users table
    
  Returns:
    str: Formatted display name
    
  Example:
    >>> format_user_display_name({'first_name': 'John', 'last_name': 'Doe', 'email': 'john@example.com'})
    'John Doe'
  """
  if not user:
    return "Guest"

  first_name = user.get('first_name', '')
  last_name = user.get('last_name', '')

  if first_name and last_name:
    return f"{first_name} {last_name}"
  elif first_name:
    return first_name
  elif last_name:
    return last_name
  else:
    # Fallback to email
    email = user.get('email', '')
    return email.split('@')[0] if email else "User"

def get_user_initials(user):
  """
  Get user initials for avatar display.
  
  Args:
    user (dict): User row
    
  Returns:
    str: User initials (max 2 characters)
    
  Example:
    >>> get_user_initials({'first_name': 'John', 'last_name': 'Doe'})
    'JD'
  """
  if not user:
    return "?"

  first_name = user.get('first_name', '')
  last_name = user.get('last_name', '')
  email = user.get('email', '')

  if first_name and last_name:
    return f"{first_name[0]}{last_name[0]}".upper()
  elif first_name:
    return first_name[0:2].upper()
  elif email:
    return email[0:2].upper()
  else:
    return "U"

def format_role_display(role):
  """
  Format user role for display.
  
  Args:
    role (str): User role ('owner', 'manager', 'staff', 'customer')
    
  Returns:
    str: Formatted role with emoji
    
  Example:
    >>> format_role_display('owner')
    '👑 Owner'
  """
  role_map = {
    'owner': '👑 Owner',
    'manager': '⭐ Manager',
    'staff': '👤 Staff',
    'customer': '🛍️ Customer',
    'admin': '🔑 Admin'
  }

  return role_map.get(role, role.title())

def check_permission(user, required_role):
  """
  Check if user has required role permission.
  
  Args:
    user (dict): User row
    required_role (str or list): Required role(s)
    
  Returns:
    bool: True if user has permission
    
  Example:
    >>> check_permission(user, 'owner')
    True
    >>> check_permission(user, ['owner', 'manager'])
    True
  """
  if not user:
    return False

  user_role = user.get('role', 'customer')

  if isinstance(required_role, str):
    required_role = [required_role]

  return user_role in required_role

def show_auth_notification(message, style='info'):
  """
  Show styled notification for auth actions.
  
  Args:
    message (str): Notification message
    style (str): 'success', 'warning', 'error', 'info'
    
  Example:
    >>> show_auth_notification("Login successful!", "success")
  """
  try:
    Notification(message, style=style).show()
  except:
    alert(message)

def get_password_strength_color(strength):
  """
  Get color for password strength indicator.
  
  Args:
    strength (str): 'weak', 'medium', 'strong'
    
  Returns:
    str: Color hex code
    
  Example:
    >>> get_password_strength_color('strong')
    '#4CAF50'
  """
  strength_colors = {
    'weak': '#F44336',      # Red
    'medium': '#FF9800',    # Orange
    'strong': '#4CAF50'     # Green
  }

  return strength_colors.get(strength, '#999999')

def format_last_login(last_login_time):
  """
  Format last login time for display.
  
  Args:
    last_login_time (datetime): Last login timestamp
    
  Returns:
    str: Formatted time string
    
  Example:
    >>> format_last_login(datetime.now() - timedelta(hours=2))
    '2 hours ago'
  """
  if not last_login_time:
    return "Never"

  from datetime import datetime, timedelta

  now = datetime.now()
  diff = now - last_login_time

  if diff.days > 365:
    years = diff.days // 365
    return f"{years} year{'s' if years > 1 else ''} ago"
  elif diff.days > 30:
    months = diff.days // 30
    return f"{months} month{'s' if months > 1 else ''} ago"
  elif diff.days > 0:
    return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
  elif diff.seconds > 3600:
    hours = diff.seconds // 3600
    return f"{hours} hour{'s' if hours > 1 else ''} ago"
  elif diff.seconds > 60:
    minutes = diff.seconds // 60
    return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
  else:
    return "Just now"

def validate_username(username):
  """
  Validate username format.
  
  Args:
    username (str): Username to validate
    
  Returns:
    tuple: (is_valid, error_message)
    
  Rules:
    - 3-20 characters
    - Alphanumeric and underscores only
    - Cannot start with number
  """
  if not username:
    return (False, "Username is required")

  if len(username) < 3:
    return (False, "Username must be at least 3 characters")

  if len(username) > 20:
    return (False, "Username must be less than 20 characters")

  if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username):
    return (False, "Username must start with a letter and contain only letters, numbers, and underscores")

  return (True, None)

def format_account_status(status):
  """
  Format account status for display.
  
  Args:
    status (str): Account status
    
  Returns:
    str: Formatted status with indicator
    
  Example:
    >>> format_account_status('active')
    '✅ Active'
  """
  status_map = {
    'active': '✅ Active',
    'inactive': '⏸ Inactive',
    'suspended': '🚫 Suspended',
    'pending': '⏳ Pending Verification'
  }

  return status_map.get(status, status.title())

def sanitize_user_input(text, max_length=255):
  """
  Sanitize user text input.
  
  Args:
    text (str): User input
    max_length (int): Maximum length
    
  Returns:
    str: Sanitized text
  """
  if not text:
    return ""

  # Remove leading/trailing whitespace
  text = text.strip()

  # Truncate to max length
  if len(text) > max_length:
    text = text[:max_length]

  return text

def create_password_requirements_text():
  """
  Get password requirements text for display.
  
  Returns:
    str: Requirements text
  """
  return """Password must:
• Be at least 8 characters long
• Contain at least one letter
• Contain at least one number
• Optionally include special characters for stronger security"""

def check_login_required(form_name):
  """
  Check if user is logged in, redirect if not.
  
  Args:
    form_name (str): Name of form requiring login
    
  Returns:
    user: User object if logged in, redirects if not
    
  Example:
    >>> user = check_login_required("Dashboard")
    >>> if user:
    >>>     # Continue with form
  """
  user = anvil.users.get_user()

  if not user:
    alert("Please login to continue")
    open_form('auth.LoginForm')
    return None

  return user

# Export all functions
__all__ = [
  'validate_email',
  'validate_password',
  'check_passwords_match',
  'format_user_display_name',
  'get_user_initials',
  'format_role_display',
  'check_permission',
  'show_auth_notification',
  'get_password_strength_color',
  'format_last_login',
  'validate_username',
  'format_account_status',
  'sanitize_user_input',
  'create_password_requirements_text',
  'check_login_required'
]
```