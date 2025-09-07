#!/usr/bin/env python3
"""
Тестовый файл для проверки исправлений ModuleNotFoundError: No module named 'cgi'
"""

import sys
import traceback

def test_imports():
    """Тестирует все основные импорты"""
    print("🧪 Тестирование импортов...")
    
    try:
        import feedparser
        print(f"✅ feedparser {feedparser.__version__} - OK")
    except Exception as e:
        print(f"❌ feedparser - FAILED: {e}")
        return False
    
    try:
        import requests
        print(f"✅ requests {requests.__version__} - OK")
    except Exception as e:
        print(f"❌ requests - FAILED: {e}")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print(f"✅ beautifulsoup4 - OK")
    except Exception as e:
        print(f"❌ beautifulsoup4 - FAILED: {e}")
        return False
    
    try:
        import aiohttp
        print(f"✅ aiohttp {aiohttp.__version__} - OK")
    except Exception as e:
        print(f"❌ aiohttp - FAILED: {e}")
        return False
    
    try:
        import schedule
        print(f"✅ schedule - OK")
    except Exception as e:
        print(f"❌ schedule - FAILED: {e}")
        return False
    
    try:
        from dotenv import load_dotenv
        print(f"✅ python-dotenv - OK")
    except Exception as e:
        print(f"❌ python-dotenv - FAILED: {e}")
        return False
    
    return True

def test_news_scraper():
    """Тестирует модуль парсинга новостей"""
    print("\n🧪 Тестирование news_scraper...")
    
    try:
        from news_scraper import LiteratureNewsScraper, NewsItem
        print("✅ Импорт news_scraper - OK")
        
        scraper = LiteratureNewsScraper()
        print("✅ Создание LiteratureNewsScraper - OK")
        
        # Тестируем создание NewsItem
        from datetime import datetime
        test_item = NewsItem(
            title="Test News",
            description="Test Description",
            url="https://example.com",
            published=datetime.now(),
            source="Test Source"
        )
        print("✅ Создание NewsItem - OK")
        
        # Тестируем фильтрацию по ключевым словам
        test_result = scraper.is_literature_related("This is a book about literature")
        if test_result:
            print("✅ Фильтрация по ключевым словам - OK")
        else:
            print("❌ Фильтрация по ключевым словам - FAILED")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ news_scraper - FAILED: {e}")
        traceback.print_exc()
        return False

def test_config():
    """Тестирует конфигурацию"""
    print("\n🧪 Тестирование config...")
    
    try:
        from config import LITERATURE_RSS_FEEDS, LITERATURE_KEYWORDS, USER_AGENT
        print("✅ Импорт config - OK")
        
        print(f"✅ RSS каналов: {len(LITERATURE_RSS_FEEDS)}")
        print(f"✅ Ключевых слов: {len(LITERATURE_KEYWORDS)}")
        print(f"✅ User-Agent настроен")
        
        return True
        
    except Exception as e:
        print(f"❌ config - FAILED: {e}")
        traceback.print_exc()
        return False

def test_rss_parsing():
    """Тестирует парсинг RSS"""
    print("\n🧪 Тестирование RSS парсинга...")
    
    try:
        from news_scraper import LiteratureNewsScraper
        scraper = LiteratureNewsScraper()
        
        # Тестируем с одним надежным RSS каналом
        test_feed = 'https://www.theguardian.com/books/rss'
        news_items = scraper.parse_rss_feed(test_feed)
        
        print(f"✅ RSS парсинг - OK (найдено {len(news_items)} новостей)")
        
        if news_items:
            sample = news_items[0]
            print(f"   Пример: {sample.title[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ RSS парсинг - FAILED: {e}")
        traceback.print_exc()
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Тестирование исправлений для ModuleNotFoundError: No module named 'cgi'")
    print(f"🐍 Python версия: {sys.version}")
    print("=" * 70)
    
    tests = [
        ("Импорты", test_imports),
        ("Конфигурация", test_config),
        ("News Scraper", test_news_scraper),
        ("RSS Парсинг", test_rss_parsing),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} - PASSED")
            else:
                print(f"❌ {test_name} - FAILED")
        except Exception as e:
            print(f"❌ {test_name} - FAILED: {e}")
    
    print("=" * 70)
    print(f"📊 Результаты: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены! Исправления работают корректно.")
        return True
    else:
        print("⚠️  Некоторые тесты не пройдены. Проверьте ошибки выше.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)