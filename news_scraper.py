import asyncio
import aiohttp
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import logging
from typing import List, Dict, Optional
import re
import html
from urllib.parse import urljoin, urlparse

from config import (
    LITERATURE_RSS_FEEDS, 
    LITERATURE_KEYWORDS, 
    NEWS_API_KEY, 
    USER_AGENT,
    MAX_NEWS_PER_UPDATE
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsItem:
    def __init__(self, title: str, description: str, url: str, published: datetime, source: str):
        self.title = title
        self.description = description
        self.url = url
        self.published = published
        self.source = source
    
    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'published': self.published.isoformat(),
            'source': self.source
        }

class LiteratureNewsScraper:
    def __init__(self):
        self.session = None
        self.sent_news_file = 'sent_news.json'
        self.sent_news_urls = self.load_sent_news()
    
    def load_sent_news(self) -> set:
        """Загружает список уже отправленных новостей"""
        try:
            with open(self.sent_news_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data.get('sent_urls', []))
        except FileNotFoundError:
            return set()
    
    def save_sent_news(self):
        """Сохраняет список отправленных новостей"""
        data = {
            'sent_urls': list(self.sent_news_urls),
            'last_update': datetime.now().isoformat()
        }
        with open(self.sent_news_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def is_literature_related(self, text: str) -> bool:
        """Проверяет, связан ли текст с литературой"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in LITERATURE_KEYWORDS)
    
    async def create_session(self):
        """Создает aiohttp сессию"""
        if not self.session:
            headers = {'User-Agent': USER_AGENT}
            self.session = aiohttp.ClientSession(headers=headers)
    
    async def close_session(self):
        """Закрывает aiohttp сессию"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def parse_rss_feed(self, feed_url: str) -> List[NewsItem]:
        """Парсит RSS канал"""
        try:
            logger.info(f"Parsing RSS feed: {feed_url}")
            
            # Используем requests для получения RSS с правильными заголовками
            headers = {'User-Agent': USER_AGENT}
            response = requests.get(feed_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Парсим RSS с помощью feedparser
            feed = feedparser.parse(response.content)
            
            if not hasattr(feed, 'entries') or not feed.entries:
                logger.warning(f"No entries found in RSS feed: {feed_url}")
                return []
            
            news_items = []
            for entry in feed.entries:
                try:
                    # Проверяем, связана ли новость с литературой
                    title = entry.get('title', '')
                    description = entry.get('description', '') or entry.get('summary', '')
                    
                    # Декодируем HTML entities
                    title = html.unescape(title) if title else ''
                    description = html.unescape(description) if description else ''
                    
                    if not self.is_literature_related(f"{title} {description}"):
                        continue
                    
                    # Парсим дату
                    published = datetime.now()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        try:
                            published = datetime(*entry.published_parsed[:6])
                        except (TypeError, ValueError):
                            # Пробуем альтернативные поля даты
                            if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                                try:
                                    published = datetime(*entry.updated_parsed[:6])
                                except:
                                    pass
                    
                    # Проверяем, что новость не старше 48 часов (увеличиваем окно)
                    if (datetime.now() - published).days > 2:
                        continue
                    
                    url = entry.get('link', '')
                    if not url or url in self.sent_news_urls:
                        continue
                    
                    # Очищаем описание от HTML тегов
                    if description:
                        soup = BeautifulSoup(description, 'html.parser')
                        description = soup.get_text().strip()
                        # Убираем лишние пробелы и переносы строк
                        description = ' '.join(description.split())
                        # Ограничиваем длину описания
                        if len(description) > 300:
                            description = description[:297] + "..."
                    
                    source = feed.feed.get('title', 'RSS Feed')
                    if hasattr(feed, 'feed') and hasattr(feed.feed, 'title'):
                        source = feed.feed.title
                    
                    news_items.append(NewsItem(title, description, url, published, source))
                    
                except Exception as entry_error:
                    logger.warning(f"Error processing RSS entry: {str(entry_error)}")
                    continue
            
            logger.info(f"Found {len(news_items)} relevant news items from {feed_url}")
            return news_items
            
        except requests.RequestException as e:
            logger.error(f"Network error parsing RSS feed {feed_url}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error parsing RSS feed {feed_url}: {str(e)}")
            return []
    
    async def search_news_api(self, query: str = "literature OR books OR author OR novel") -> List[NewsItem]:
        """Ищет новости через News API"""
        if not NEWS_API_KEY:
            logger.info("News API key not provided, skipping News API search")
            return []
        
        try:
            await self.create_session()
            
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'language': 'en,ru',
                'sortBy': 'publishedAt',
                'from': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                'apiKey': NEWS_API_KEY,
                'pageSize': 20
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    news_items = []
                    
                    for article in data.get('articles', []):
                        title = article.get('title', '')
                        description = article.get('description', '')
                        url = article.get('url', '')
                        
                        if not self.is_literature_related(f"{title} {description}"):
                            continue
                        
                        if url in self.sent_news_urls:
                            continue
                        
                        published_str = article.get('publishedAt', '')
                        try:
                            published = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
                        except:
                            published = datetime.now()
                        
                        source = article.get('source', {}).get('name', 'News API')
                        
                        news_items.append(NewsItem(title, description, url, published, source))
                    
                    return news_items
                else:
                    logger.error(f"News API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error searching News API: {str(e)}")
            return []
    
    async def get_latest_literature_news(self) -> List[NewsItem]:
        """Получает последние новости о литературе из всех источников"""
        all_news = []
        successful_feeds = 0
        
        # Парсим RSS каналы
        logger.info(f"Processing {len(LITERATURE_RSS_FEEDS)} RSS feeds...")
        for i, feed_url in enumerate(LITERATURE_RSS_FEEDS):
            try:
                logger.info(f"Processing feed {i+1}/{len(LITERATURE_RSS_FEEDS)}: {feed_url}")
                news_items = self.parse_rss_feed(feed_url)
                if news_items:
                    all_news.extend(news_items)
                    successful_feeds += 1
                    logger.info(f"✅ Successfully processed {len(news_items)} items from {feed_url}")
                else:
                    logger.info(f"ℹ️  No relevant news found in {feed_url}")
            except Exception as e:
                logger.error(f"❌ Failed to process feed {feed_url}: {str(e)}")
                continue
        
        logger.info(f"Successfully processed {successful_feeds}/{len(LITERATURE_RSS_FEEDS)} RSS feeds")
        
        # Ищем через News API
        try:
            api_news = await self.search_news_api()
            if api_news:
                all_news.extend(api_news)
                logger.info(f"✅ Added {len(api_news)} items from News API")
        except Exception as e:
            logger.error(f"❌ News API search failed: {str(e)}")
        
        # Убираем дубликаты по URL
        seen_urls = set()
        unique_news = []
        for news in all_news:
            if news.url and news.url not in seen_urls:
                seen_urls.add(news.url)
                unique_news.append(news)
        
        logger.info(f"Found {len(unique_news)} unique news items after deduplication")
        
        # Сортируем по дате публикации (новые сначала)
        unique_news.sort(key=lambda x: x.published, reverse=True)
        
        # Ограничиваем количество новостей
        final_news = unique_news[:MAX_NEWS_PER_UPDATE]
        logger.info(f"Returning {len(final_news)} news items (limited by MAX_NEWS_PER_UPDATE={MAX_NEWS_PER_UPDATE})")
        
        return final_news
    
    def mark_news_as_sent(self, news_items: List[NewsItem]):
        """Отмечает новости как отправленные"""
        for news in news_items:
            self.sent_news_urls.add(news.url)
        self.save_sent_news()

# Функция для тестирования
async def test_scraper():
    scraper = LiteratureNewsScraper()
    try:
        news = await scraper.get_latest_literature_news()
        print(f"Found {len(news)} literature news items:")
        for item in news[:3]:  # Показываем только первые 3
            print(f"- {item.title}")
            print(f"  Source: {item.source}")
            print(f"  URL: {item.url}")
            print()
    finally:
        await scraper.close_session()

if __name__ == "__main__":
    asyncio.run(test_scraper())