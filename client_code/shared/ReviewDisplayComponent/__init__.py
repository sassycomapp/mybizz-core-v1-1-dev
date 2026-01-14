from ._anvil_designer import ReviewDisplayComponentTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class ReviewDisplayComponent(ReviewDisplayComponentTemplate):
  """Display approved reviews with ratings and responses"""

  def __init__(self, item_type=None, item_id=None, **properties):
    self.item_type = item_type  # 'product', 'service', 'booking'
    self.item_id = item_id
    self.reviews = []
    self.page = 1
    self.page_size = 10

    self.init_components(**properties)

    # Configure sort dropdown
    self.dd_sort.items = [
      ('Most Recent', 'recent'),
      ('Highest Rated', 'highest'),
      ('Lowest Rated', 'lowest'),
      ('Most Helpful', 'helpful')
    ]
    self.dd_sort.selected_value = 'recent'

    # Configure load more button
    self.btn_load_more.text = "Load More Reviews"
    self.btn_load_more.role = "outlined-button"
    self.btn_load_more.visible = False

    # Load reviews
    self.load_reviews()

  def load_reviews(self):
    """Load reviews for item"""
    if not self.item_type or not self.item_id:
      self.lbl_rating_summary.text = "No reviews available"
      return

    try:
      sort_by = self.dd_sort.selected_value

      result = anvil.server.call(
        'get_reviews',
        self.item_type,
        self.item_id,
        status='approved',
        sort_by=sort_by,
        page=self.page,
        page_size=self.page_size
      )

      if result['success']:
        self.reviews = result['data']['reviews']
        total_reviews = result['data']['total']
        avg_rating = result['data']['avg_rating']

        # Update rating summary
        stars = '⭐' * int(avg_rating)
        self.lbl_rating_summary.text = f"{stars} {avg_rating:.1f} / 5.0 ({total_reviews} reviews)"
        self.lbl_rating_summary.font_size = 18
        self.lbl_rating_summary.bold = True

        # Load reviews into repeating panel
        self.rp_reviews.items = self.reviews

        # Show/hide load more button
        self.btn_load_more.visible = len(self.reviews) < total_reviews

      else:
        self.lbl_rating_summary.text = "No reviews available"

    except Exception as e:
      print(f"Error loading reviews: {e}")
      alert(f"Failed to load reviews: {str(e)}")

  def dropdown_sort_change(self, **event_args):
    """Re-load reviews when sort changes"""
    self.page = 1
    self.reviews = []
    self.load_reviews()

  def button_load_more_click(self, **event_args):
    """Load next page of reviews"""
    self.page += 1

    try:
      result = anvil.server.call(
        'get_reviews',
        self.item_type,
        self.item_id,
        status='approved',
        sort_by=self.dd_sort.selected_value,
        page=self.page,
        page_size=self.page_size
      )

      if result['success']:
        new_reviews = result['data']['reviews']
        self.reviews.extend(new_reviews)
        self.rp_reviews.items = self.reviews

        # Hide button if no more reviews
        total_reviews = result['data']['total']
        self.btn_load_more.visible = len(self.reviews) < total_reviews

    except Exception as e:
      print(f"Error loading more reviews: {e}")
      alert(f"Failed to load more reviews: {str(e)}")

  @handle("dd_sort", "change")
  def dd_sort_change(self, **event_args):
    """This method is called when an item is selected"""
    pass

  @handle("btn_load_more", "click")
  def btn_load_more_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
