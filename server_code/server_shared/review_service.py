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