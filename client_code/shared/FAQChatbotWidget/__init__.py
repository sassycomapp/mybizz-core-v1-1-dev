from ._anvil_designer import FAQChatbotWidgetTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import stripe.checkout
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class FAQChatbotWidget(FAQChatbotWidgetTemplate):
  """Simple FAQ chatbot with keyword matching"""

  def __init__(self, **properties):
    self.conversation = []
    self.is_open = False
    self.init_components(**properties)

    # Initial state: closed (chat button)
    self.col_chat_window.visible = False
    self.btn_chat_toggle.text = "💬 Help"
    self.btn_chat_toggle.role = "primary-color"

    # Configure close button
    self.btn_close.text = "✕"
    self.btn_close.role = "secondary-color"

    # Configure input
    self.txt_question.placeholder = "Type your question..."

    # Configure buttons
    self.btn_send.text = "Send"
    self.btn_send.icon = "fa:paper-plane"
    self.btn_send.role = "primary-color"

    self.btn_submit_ticket.text = "Submit a Support Ticket"
    self.btn_submit_ticket.role = "outlined-button"

    # Add welcome message
    self.add_bot_message("Hi! I'm here to help. Ask me anything!")

  def add_bot_message(self, message, articles=None):
    """Add bot message to conversation"""
    msg = {
      'type': 'bot',
      'text': message,
      'articles': articles
    }

    self.conversation.append(msg)
    self.refresh_conversation()

  def add_user_message(self, message):
    """Add user message to conversation"""
    msg = {
      'type': 'user',
      'text': message
    }

    self.conversation.append(msg)
    self.refresh_conversation()

  def refresh_conversation(self):
    """Refresh conversation display"""
    self.rp_messages.items = self.conversation

    # Scroll to bottom (requires custom JavaScript)
    # Add this to Native Libraries: scrollToBottom function

  def button_chat_toggle_click(self, **event_args):
    """Toggle chat window"""
    self.is_open = not self.is_open

    if self.is_open:
      self.col_chat_window.visible = True
      self.btn_chat_toggle.visible = False
    else:
      self.col_chat_window.visible = False
      self.btn_chat_toggle.visible = True

  def button_close_click(self, **event_args):
    """Close chat window"""
    self.button_chat_toggle_click()

  def button_send_click(self, **event_args):
    """Send user question"""
    question = self.txt_question.text.strip()

    if not question:
      return

    # Add user message
    self.add_user_message(question)

    # Clear input
    self.txt_question.text = ''

    # Query chatbot
    try:
      result = anvil.server.call('ask_chatbot', question)

      if result['found']:
        # Bot found answers
        articles = result['answers']

        response = "I found these articles that might help:"
        self.add_bot_message(response, articles)
      else:
        # No answers found
        self.add_bot_message(
          "I couldn't find an answer to that. Would you like to submit a support ticket?"
        )

    except Exception as e:
      print(f"Chatbot error: {e}")
      self.add_bot_message("Sorry, I'm having trouble right now. Please try again.")

  @handle("txt_question", "pressed_enter")
  def txt_question_pressed_enter(self, **event_args):
    """Send on Enter key"""
    self.button_send_click()

  def button_submit_ticket_click(self, **event_args):
    """Open ticket submission form"""
    from ..shared.TicketSubmissionForm import TicketSubmissionForm

    ticket_form = TicketSubmissionForm()
    alert(ticket_form, large=True, title="Submit Support Ticket")

  @handle("btn_chat_toggle", "click")
  def btn_chat_toggle_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_close", "click")
  def btn_close_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_send", "click")
  def btn_send_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass

  @handle("btn_submit_ticket", "click")
  def btn_submit_ticket_click(self, **event_args):
    """This method is called when the button is clicked"""
    pass
