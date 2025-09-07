import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')

# News API Configuration
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

# Bot Settings
UPDATE_INTERVAL_HOURS = int(os.getenv('UPDATE_INTERVAL_HOURS', 6))
MAX_NEWS_PER_UPDATE = int(os.getenv('MAX_NEWS_PER_UPDATE', 5))

# RSS Feeds for Literature News
LITERATURE_RSS_FEEDS = [
    'https://www.theguardian.com/books/rss',
    'https://lithub.com/feed/',
    'https://feeds.feedburner.com/goodreads/blog',
    'https://bookmarks.reviews/feed/',
    'https://www.publishersweekly.com/rss/latest-articles.xml',
    'https://rss.cnn.com/rss/edition.rss',  # Общие новости, будут фильтроваться
    'https://feeds.bbci.co.uk/news/rss.xml',  # BBC News
    'https://www.npr.org/rss/rss.php?id=1008',  # NPR Books
]

# Keywords for filtering literature news
LITERATURE_KEYWORDS = [
    'книга', 'книги', 'автор', 'писатель', 'роман', 'поэзия', 'литература',
    'издательство', 'публикация', 'рецензия', 'бестселлер', 'премия',
    'book', 'books', 'author', 'writer', 'novel', 'poetry', 'literature',
    'publisher', 'publishing', 'review', 'bestseller', 'award', 'fiction',
    'non-fiction', 'memoir', 'biography', 'anthology', 'manuscript'
]

# User Agent for web scraping
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'