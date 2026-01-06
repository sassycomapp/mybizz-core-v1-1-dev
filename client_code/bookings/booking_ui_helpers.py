import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
from datetime import datetime, timedelta, time
from anvil import *

"""
Booking UI Helper Functions
Reusable utilities for booking-related UI operations
"""

def format_booking_status(status):
  """
  Format booking status with emoji.
  
  Args:
    status (str): Booking status
    
  Returns:
    str: Formatted status
    
  Example:
    >>> format_booking_status('confirmed')
    '✅ Confirmed'
  """
  status_map = {
    'pending': '⏳ Pending',
    'confirmed': '✅ Confirmed',
    'cancelled': '❌ Cancelled',
    'completed': '✔️ Completed',
    'no_show': '👻 No Show',
    'in_progress': '🔄 In Progress'
  }

  return status_map.get(status, status.title())

def get_booking_status_color(status):
  """
  Get color for booking status.
  
  Args:
    status (str): Booking status
    
  Returns:
    str: Color code
  """
  color_map = {
    'pending': '#FF9800',      # Orange
    'confirmed': '#4CAF50',    # Green
    'cancelled': '#F44336',    # Red
    'completed': '#2196F3',    # Blue
    'no_show': '#9E9E9E',      # Gray
    'in_progress': '#00BCD4'   # Cyan
  }

  return color_map.get(status, '#000000')

def format_date_range(start_date, end_date):
  """
  Format date range for display.
  
  Args:
    start_date (datetime): Start date
    end_date (datetime): End date
    
  Returns:
    str: Formatted date range
    
  Example:
    >>> format_date_range(datetime(2026, 1, 5), datetime(2026, 1, 8))
    'Jan 5 - Jan 8, 2026'
  """
  if not start_date:
    return "No dates"

  if not end_date or start_date.date() == end_date.date():
    return start_date.strftime('%b %d, %Y')

  if start_date.year == end_date.year:
    if start_date.month == end_date.month:
      return f"{start_date.strftime('%b %d')} - {end_date.strftime('%d, %Y')}"
    else:
      return f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
  else:
    return f"{start_date.strftime('%b %d, %Y')} - {end_date.strftime('%b %d, %Y')}"

def format_time_slot(start_time, end_time):
  """
  Format time slot for display.
  
  Args:
    start_time (datetime or time): Start time
    end_time (datetime or time): End time
    
  Returns:
    str: Formatted time slot
    
  Example:
    >>> format_time_slot(time(9, 0), time(10, 0))
    '9:00 AM - 10:00 AM'
  """
  if isinstance(start_time, datetime):
    start_time = start_time.time()
  if isinstance(end_time, datetime):
    end_time = end_time.time()

  start_str = start_time.strftime('%I:%M %p').lstrip('0')
  end_str = end_time.strftime('%I:%M %p').lstrip('0')

  return f"{start_str} - {end_str}"

def calculate_duration(start_time, end_time):
  """
  Calculate duration between times.
  
  Args:
    start_time (datetime): Start time
    end_time (datetime): End time
    
  Returns:
    str: Formatted duration
    
  Example:
    >>> calculate_duration(datetime(2026, 1, 5, 9, 0), datetime(2026, 1, 5, 11, 30))
    '2.5 hours'
  """
  if not start_time or not end_time:
    return "Unknown"

  duration = end_time - start_time
  hours = duration.total_seconds() / 3600

  if hours >= 24:
    days = hours / 24
    return f"{days:.1f} days"
  elif hours >= 1:
    if hours == int(hours):
      return f"{int(hours)} hour{'s' if hours > 1 else ''}"
    else:
      return f"{hours:.1f} hours"
  else:
    minutes = duration.total_seconds() / 60
    return f"{int(minutes)} minutes"

def get_available_time_slots(date, resource_id, duration_minutes=60):
  """
  Generate available time slots for a date.
  
  Args:
    date (datetime.date): Date to check
    resource_id (str): Resource ID to check availability
    duration_minutes (int): Duration of each slot
    
  Returns:
    list: Available time slots
    
  Example:
    >>> slots = get_available_time_slots(date.today(), resource_id, 60)
    [{'start': time(9, 0), 'end': time(10, 0), 'available': True}, ...]
  """
  # This would typically call a server function
  # Placeholder implementation
  slots = []
  start_hour = 9  # 9 AM
  end_hour = 17   # 5 PM

  current_time = time(start_hour, 0)

  while current_time.hour < end_hour:
    slot_end = (datetime.combine(date, current_time) + timedelta(minutes=duration_minutes)).time()

    slots.append({
      'start': current_time,
      'end': slot_end,
      'available': True,
      'label': format_time_slot(current_time, slot_end)
    })

    # Move to next slot
    current_time = slot_end

  return slots

def is_booking_upcoming(booking_date):
  """
  Check if booking is upcoming (in future).
  
  Args:
    booking_date (datetime): Booking date
    
  Returns:
    bool: True if upcoming
  """
  if not booking_date:
    return False

  now = datetime.now()
  return booking_date > now

def is_booking_past(booking_date):
  """
  Check if booking is in the past.
  
  Args:
    booking_date (datetime): Booking date
    
  Returns:
    bool: True if past
  """
  if not booking_date:
    return False

  now = datetime.now()
  return booking_date < now

def format_booking_reference(booking_id_or_number):
  """
  Format booking reference number.
  
  Args:
    booking_id_or_number: Booking ID or number
    
  Returns:
    str: Formatted reference
    
  Example:
    >>> format_booking_reference("BK123456")
    'BK-123456'
  """
  ref = str(booking_id_or_number)

  if not ref.startswith('BK'):
    ref = f"BK{ref}"

  # Add hyphen after BK
  if len(ref) > 2 and ref[2] != '-':
    ref = f"{ref[:2]}-{ref[2:]}"

  return ref

def calculate_nights(check_in, check_out):
  """
  Calculate number of nights for accommodation.
  
  Args:
    check_in (datetime.date): Check-in date
    check_out (datetime.date): Check-out date
    
  Returns:
    int: Number of nights
    
  Example:
    >>> calculate_nights(date(2026, 1, 5), date(2026, 1, 8))
    3
  """
  if not check_in or not check_out:
    return 0

  delta = check_out - check_in
  return max(0, delta.days)

def format_guest_count(adults, children=0):
  """
  Format guest count display.
  
  Args:
    adults (int): Number of adults
    children (int): Number of children
    
  Returns:
    str: Formatted guest count
    
  Example:
    >>> format_guest_count(2, 1)
    '2 adults, 1 child'
  """
  parts = []

  if adults:
    parts.append(f"{adults} adult{'s' if adults > 1 else ''}")

  if children:
    parts.append(f"{children} child{'ren' if children > 1 else ''}")

  return ', '.join(parts) if parts else '0 guests'

def validate_booking_dates(check_in, check_out):
  """
  Validate booking date selection.
  
  Args:
    check_in (datetime.date): Check-in date
    check_out (datetime.date): Check-out date
    
  Returns:
    tuple: (is_valid, error_message)
  """
  if not check_in:
    return (False, "Check-in date is required")

  if not check_out:
    return (False, "Check-out date is required")

  if check_in >= check_out:
    return (False, "Check-out must be after check-in")

  # Check if dates are in the past
  today = datetime.now().date()
  if check_in < today:
    return (False, "Check-in date cannot be in the past")

  # Check if dates are too far in future (e.g., 2 years)
  max_advance = today + timedelta(days=730)
  if check_in > max_advance:
    return (False, "Cannot book more than 2 years in advance")

  return (True, None)

def get_booking_urgency(booking_date):
  """
  Get urgency level for upcoming booking.
  
  Args:
    booking_date (datetime): Booking date
    
  Returns:
    str: 'urgent', 'soon', 'normal'
    
  Example:
    >>> get_booking_urgency(datetime.now() + timedelta(hours=2))
    'urgent'
  """
  if not booking_date:
    return 'normal'

  now = datetime.now()
  delta = booking_date - now
  hours = delta.total_seconds() / 3600

  if hours < 0:
    return 'past'
  elif hours < 4:
    return 'urgent'
  elif hours < 24:
    return 'soon'
  else:
    return 'normal'

def format_cancellation_deadline(booking_date, hours_before=24):
  """
  Calculate and format cancellation deadline.
  
  Args:
    booking_date (datetime): Booking date
    hours_before (int): Hours before booking to allow cancellation
    
  Returns:
    str: Formatted deadline
  """
  if not booking_date:
    return "Unknown"

  deadline = booking_date - timedelta(hours=hours_before)
  now = datetime.now()

  if now > deadline:
    return "Cancellation deadline passed"

  return f"Cancel before {deadline.strftime('%b %d at %I:%M %p')}"

def calculate_booking_price(base_price, nights_or_duration, discount_percent=0):
  """
  Calculate total booking price.
  
  Args:
    base_price (float): Price per night/unit
    nights_or_duration (int): Number of nights or units
    discount_percent (float): Discount percentage
    
  Returns:
    dict: {'subtotal': float, 'discount': float, 'total': float}
  """
  subtotal = base_price * nights_or_duration
  discount = subtotal * (discount_percent / 100)
  total = subtotal - discount

  return {
    'subtotal': subtotal,
    'discount': discount,
    'total': total
  }

def show_booking_notification(message, style='info'):
  """
  Show styled notification for booking actions.
  
  Args:
    message (str): Notification message
    style (str): 'success', 'warning', 'error', 'info'
  """
  try:
    Notification(message, style=style).show()
  except:
    alert(message)

def format_resource_name(resource):
  """
  Format resource name for display.
  
  Args:
    resource (dict): Resource row
    
  Returns:
    str: Formatted resource name
  """
  if not resource:
    return "No resource"

  name = resource.get('name', 'Unknown')
  resource_type = resource.get('resource_type', '')

  if resource_type:
    return f"{name} ({resource_type.title()})"

  return name

def get_booking_icon(booking_type):
  """
  Get icon for booking type.
  
  Args:
    booking_type (str): Type of booking
    
  Returns:
    str: Font Awesome icon code
  """
  icon_map = {
    'accommodation': 'fa:bed',
    'appointment': 'fa:calendar-check',
    'event': 'fa:ticket',
    'rental': 'fa:key',
    'service': 'fa:wrench',
    'class': 'fa:graduation-cap',
    'tour': 'fa:map'
  }

  return icon_map.get(booking_type, 'fa:calendar')

# Export all functions
__all__ = [
  'format_booking_status',
  'get_booking_status_color',
  'format_date_range',
  'format_time_slot',
  'calculate_duration',
  'get_available_time_slots',
  'is_booking_upcoming',
  'is_booking_past',
  'format_booking_reference',
  'calculate_nights',
  'format_guest_count',
  'validate_booking_dates',
  'get_booking_urgency',
  'format_cancellation_deadline',
  'calculate_booking_price',
  'show_booking_notification',
  'format_resource_name',
  'get_booking_icon'
]
```