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

# server_code/shared/chatbot_service.py

# Common stopwords to ignore
STOPWORDS = ['a', 'an', 'the', 'is', 'are', 'was', 'were', 'how', 'do', 'i', 'to', 'can', 'what', 'where', 'when']

@anvil.server.callable
def ask_chatbot(user_question):
  """
  Simple keyword matching chatbot.
  
  Args:
    user_question (str): User's question
    
  Returns:
    dict: {'found': bool, 'answers': list} or {'found': bool, 'message': str}
  """
  try:
    # Extract keywords
    words = user_question.lower().split()
    keywords = [w for w in words if w not in STOPWORDS and len(w) > 2]

    if not keywords:
      return {'found': False, 'message': 'Please ask a more specific question'}

    # Search KB articles
    articles = list(app_tables.kb_articles.search(published=True))

    if not articles:
      return {'found': False, 'message': 'No knowledge base articles available'}

    # Score articles by keyword matches
    scored_articles = []

    for article in articles:
      score = 0

      # Check title (weight: 3)
      title_lower = article['title'].lower()
      score += sum(1 for kw in keywords if kw in title_lower) * 3

      # Check keywords field (weight: 2)
      article_keywords = article.get('keywords', [])
      if article_keywords:
        article_keywords_str = ' '.join(article_keywords).lower()
        score += sum(1 for kw in keywords if kw in article_keywords_str) * 2

      # Check content (weight: 1)
      content_lower = article.get('content', '').lower()
      score += sum(1 for kw in keywords if kw in content_lower)

      if score > 0:
        scored_articles.append((score, article))

    # Sort by score (highest first)
    scored_articles.sort(key=lambda x: x[0], reverse=True)

    # Return top 3 articles
    if scored_articles:
      top_articles = [
        {
          'title': article['title'],
          'excerpt': article.get('excerpt', '')[:100] + '...',
          'url': f"/help/{article['slug']}"
        }
        for score, article in scored_articles[:3]
      ]

      return {'found': True, 'answers': top_articles}
    else:
      return {'found': False, 'message': 'No matching articles found'}

  except Exception as e:
    print(f"Chatbot error: {e}")
    return {'found': False, 'message': 'Error processing question'}