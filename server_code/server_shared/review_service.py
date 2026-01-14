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

@anvil.server.callable
def get_reviews(item_type, item_id, status='approved', sort_by='recent', page=1, page_size=10):
  """
  Get reviews for item with pagination and sorting.
  
  Args:
    item_type (str): Type of item ('product', 'service', 'booking')
    item_id (str): Item ID
    status (str): Review status filter
    sort_by (str): Sort order ('recent', 'highest', 'lowest', 'helpful')
    page (int): Page number (1-indexed)
    page_size (int): Reviews per page
    
  Returns:
    dict: {'success': bool, 'data': dict} or {'success': bool, 'error': str}
  """
  try:
    # Query reviews
    reviews = list(app_tables.reviews.search(
      item_type=item_type,
      item_id=item_id,
      status=status
    ))

    if not reviews:
      return {
        'success': True,
        'data': {
          'reviews': [],
          'total': 0,
          'avg_rating': 0
        }
      }

    # Sort
    if sort_by == 'highest':
      reviews.sort(key=lambda r: r['rating'], reverse=True)
    elif sort_by == 'lowest':
      reviews.sort(key=lambda r: r['rating'])
    elif sort_by == 'helpful':
      reviews.sort(key=lambda r: r.get('helpful_count', 0), reverse=True)
    else:  # recent
      reviews.sort(key=lambda r: r['created_at'], reverse=True)

    # Calculate average rating
    avg_rating = sum(r['rating'] for r in reviews) / len(reviews)

    # Paginate
    start = (page - 1) * page_size
    end = start + page_size
    paginated_reviews = reviews[start:end]

    return {
      'success': True,
      'data': {
        'reviews': paginated_reviews,
        'total': len(reviews),
        'avg_rating': avg_rating
      }
    }

  except Exception as e:
    print(f"Error getting reviews: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
def mark_review_helpful(review_id):
  """
  Mark review as helpful.
  
  Args:
    review_id (str): Review ID
    
  Returns:
    dict: {'success': bool} or {'success': bool, 'error': str}
  """
  try:
    review = app_tables.reviews.get_by_id(review_id)

    if not review:
      return {'success': False, 'error': 'Review not found'}

    # Increment helpful count
    review['helpful_count'] = review.get('helpful_count', 0) + 1
    review.update()

    return {'success': True}

  except Exception as e:
    print(f"Error marking review helpful: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
def report_review(review_id, reason):
  """
  Report review as inappropriate.
  
  Args:
    review_id (str): Review ID
    reason (str): Report reason
    
  Returns:
    dict: {'success': bool} or {'success': bool, 'error': str}
  """
  try:
    review = app_tables.reviews.get_by_id(review_id)

    if not review:
      return {'success': False, 'error': 'Review not found'}

    # Create report record (you'll need a reports table)
    # For now, just flag the review
    review['reported'] = True
    review['report_reason'] = reason
    review['reported_at'] = datetime.now()
    review.update()

    # Optionally: Send notification to admin

    return {'success': True}

  except Exception as e:
    print(f"Error reporting review: {e}")
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def get_pending_reviews():
  """
  Get all pending reviews for moderation.
  
  Returns:
    dict: {'success': bool, 'data': list} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    # Get pending reviews
    reviews = list(app_tables.reviews.search(
      status='pending',
      tables.order_by('created_at', ascending=False)
    ))

    # Add item name for display
    for review in reviews:
      item_type = review.get('item_type')
      item_id = review.get('item_id')

      # Get item name based on type
      if item_type == 'product':
        item = app_tables.products.get_by_id(item_id)
        review['item_name'] = f"Product: {item['name']}" if item else 'Unknown Product'
      elif item_type == 'service':
        item = app_tables.services.get_by_id(item_id)
        review['item_name'] = f"Service: {item['name']}" if item else 'Unknown Service'
      elif item_type == 'booking':
        item = app_tables.bookings.get_by_id(item_id)
        review['item_name'] = f"Booking: {item.get('service_name', 'Unknown')}" if item else 'Unknown Booking'
      else:
        review['item_name'] = 'Unknown Item'

    return {'success': True, 'data': reviews}

  except Exception as e:
    print(f"Error getting pending reviews: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
@anvil.users.login_required
def approve_review(review_id):
  """
  Approve a review.
  
  Args:
    review_id (str): Review ID
    
  Returns:
    dict: {'success': bool} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    review = app_tables.reviews.get_by_id(review_id)

    if not review:
      return {'success': False, 'error': 'Review not found'}

    # Update status
    review['status'] = 'approved'
    review['moderated_by'] = user
    review['moderated_at'] = datetime.now()
    review.update()

    return {'success': True}

  except Exception as e:
    print(f"Error approving review: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
@anvil.users.login_required
def reject_review(review_id, reason=None):
  """
  Reject a review.
  
  Args:
    review_id (str): Review ID
    reason (str): Optional rejection reason
    
  Returns:
    dict: {'success': bool} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    review = app_tables.reviews.get_by_id(review_id)

    if not review:
      return {'success': False, 'error': 'Review not found'}

    # Update status
    review['status'] = 'rejected'
    review['rejection_reason'] = reason
    review['moderated_by'] = user
    review['moderated_at'] = datetime.now()
    review.update()

    return {'success': True}

  except Exception as e:
    print(f"Error rejecting review: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
@anvil.users.login_required
def mark_review_spam(review_id):
  """
  Mark review as spam.
  
  Args:
    review_id (str): Review ID
    
  Returns:
    dict: {'success': bool} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    review = app_tables.reviews.get_by_id(review_id)

    if not review:
      return {'success': False, 'error': 'Review not found'}

    # Mark as spam
    review['status'] = 'spam'
    review['moderated_by'] = user
    review['moderated_at'] = datetime.now()
    review.update()

    return {'success': True}

  except Exception as e:
    print(f"Error marking spam: {e}")
    return {'success': False, 'error': str(e)}


@anvil.server.callable
@anvil.users.login_required
def add_business_response(review_id, response):
  """
  Add business response to review.
  
  Args:
    review_id (str): Review ID
    response (str): Business response text
    
  Returns:
    dict: {'success': bool} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    if user['role'] not in ['owner', 'manager']:
      return {'success': False, 'error': 'Access denied'}

    review = app_tables.reviews.get_by_id(review_id)

    if not review:
      return {'success': False, 'error': 'Review not found'}

    # Add response
    review['business_response'] = response
    review['response_by'] = user
    review['response_at'] = datetime.now()

    # Auto-approve if not already approved
    if review['status'] == 'pending':
      review['status'] = 'approved'

    review.update()

    return {'success': True}

  except Exception as e:
    print(f"Error adding response: {e}")
    return {'success': False, 'error': str(e)}

@anvil.server.callable
@anvil.users.login_required
def submit_review(item_type, item_id, review_data):
  """
  Submit a review for moderation.
  
  Args:
    item_type (str): Type of item ('product', 'service', 'booking')
    item_id (str): Item ID
    review_data (dict): {'rating': int, 'title': str, 'comment': str}
    
  Returns:
    dict: {'success': bool} or {'success': bool, 'error': str}
  """
  try:
    user = anvil.users.get_user()

    # Check if user already reviewed this item
    existing_review = app_tables.reviews.get(
      item_type=item_type,
      item_id=item_id,
      customer_id=user
    )

    if existing_review:
      return {'success': False, 'error': 'You have already reviewed this item'}

    # Check if verified purchase
    is_verified = check_verified_purchase(user, item_type, item_id)

    # Get reviewer name
    reviewer_name = user.get('name') or user['email'].split('@')[0]

    # Create review
    app_tables.reviews.add_row(
      item_type=item_type,
      item_id=item_id,
      customer_id=user,
      reviewer_name=reviewer_name,
      rating=review_data['rating'],
      title=review_data['title'],
      comment=review_data['comment'],
      status='pending',
      is_verified_purchase=is_verified,
      helpful_count=0,
      reported=False,
      created_at=datetime.now()
    )

    return {'success': True}

  except Exception as e:
    print(f"Error submitting review: {e}")
    return {'success': False, 'error': str(e)}


def check_verified_purchase(user, item_type, item_id):
  """
  Check if user has purchased/booked this item.
  
  Args:
    user (row): User row
    item_type (str): Item type
    item_id (str): Item ID
    
  Returns:
    bool: True if verified purchase
  """
  try:
    if item_type == 'product':
      # Check if user has completed order with this product
      orders = app_tables.orders.search(
        customer_id=user,
        status='completed'
      )

      for order in orders:
        items = order.get('items', [])
        for item in items:
          if item.get('product_id') == item_id:
            return True

      return False

    elif item_type == 'service':
      # Check if user has completed service booking
      bookings = app_tables.bookings.search(
        customer_id=user,
        service_id=item_id,
        status='completed'
      )

      return len(list(bookings)) > 0

    elif item_type == 'booking':
      # Check if user owns this booking
      booking = app_tables.bookings.get_by_id(item_id)

      if booking and booking['customer_id'] == user:
        return booking['status'] == 'completed'

      return False

    return False

  except Exception as e:
    print(f"Error checking verified purchase: {e}")
    return False