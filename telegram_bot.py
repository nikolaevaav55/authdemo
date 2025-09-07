import asyncio
import logging
from datetime import datetime
from typing import List, Optional
from telegram import Bot
from telegram.error import TelegramError
from telegram.constants import ParseMode

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID
from news_scraper import NewsItem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramNewsBot:
    def __init__(self):
        if not TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables")
        if not TELEGRAM_CHANNEL_ID:
            raise ValueError("TELEGRAM_CHANNEL_ID is not set in environment variables")
        
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        self.channel_id = TELEGRAM_CHANNEL_ID
    
    def format_news_message(self, news_item: NewsItem) -> str:
        """Форматирует новость для отправки в Telegram"""
        # Экранируем специальные символы для Markdown
        def escape_markdown(text: str) -> str:
            special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
            for char in special_chars:
                text = text.replace(char, f'\\{char}')
            return text
        
        # Форматируем заголовок
        title = escape_markdown(news_item.title)
        
        # Форматируем описание
        description = ""
        if news_item.description and news_item.description.strip():
            description = escape_markdown(news_item.description[:400])  # Ограничиваем длину
            if len(news_item.description) > 400:
                description += "\\.\\.\\."
        
        # Форматируем дату
        published_date = news_item.published.strftime("%d\\.%m\\.%Y %H:%M")
        
        # Форматируем источник
        source = escape_markdown(news_item.source)
        
        # Создаем сообщение
        message = f"📚 *{title}*\n\n"
        
        if description:
            message += f"{description}\n\n"
        
        message += f"🔗 [Читать полностью]({news_item.url})\n"
        message += f"📅 {published_date} \\| 📰 {source}"
        
        return message
    
    async def send_news_to_channel(self, news_items: List[NewsItem]) -> bool:
        """Отправляет новости в канал"""
        if not news_items:
            logger.info("No news to send")
            return True
        
        success_count = 0
        
        try:
            for news_item in news_items:
                try:
                    message = self.format_news_message(news_item)
                    
                    await self.bot.send_message(
                        chat_id=self.channel_id,
                        text=message,
                        parse_mode=ParseMode.MARKDOWN_V2,
                        disable_web_page_preview=False
                    )
                    
                    success_count += 1
                    logger.info(f"Successfully sent news: {news_item.title[:50]}...")
                    
                    # Небольшая пауза между сообщениями, чтобы не превысить лимиты API
                    await asyncio.sleep(1)
                    
                except TelegramError as e:
                    logger.error(f"Failed to send news '{news_item.title[:50]}...': {str(e)}")
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error sending news '{news_item.title[:50]}...': {str(e)}")
                    continue
            
            logger.info(f"Successfully sent {success_count}/{len(news_items)} news items")
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error sending news to channel: {str(e)}")
            return False
    
    async def send_status_message(self, message: str):
        """Отправляет статусное сообщение в канал"""
        try:
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=f"🤖 *Статус бота*\n\n{message}",
                parse_mode=ParseMode.MARKDOWN_V2
            )
            logger.info("Status message sent successfully")
        except Exception as e:
            logger.error(f"Failed to send status message: {str(e)}")
    
    async def test_connection(self) -> bool:
        """Тестирует подключение к боту и каналу"""
        try:
            # Проверяем, что бот работает
            bot_info = await self.bot.get_me()
            logger.info(f"Bot connected successfully: @{bot_info.username}")
            
            # Пробуем отправить тестовое сообщение
            test_message = f"🧪 *Тест подключения*\n\nБот успешно подключен\\!\nВремя: {datetime.now().strftime('%d\\.%m\\.%Y %H:%M:%S')}"
            
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=test_message,
                parse_mode=ParseMode.MARKDOWN_V2
            )
            
            logger.info("Test message sent successfully")
            return True
            
        except TelegramError as e:
            logger.error(f"Telegram API error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
    
    async def send_daily_summary(self, news_count: int):
        """Отправляет ежедневную сводку"""
        try:
            current_time = datetime.now().strftime("%d\\.%m\\.%Y")
            message = f"📊 *Ежедневная сводка*\n\n"
            message += f"📅 Дата: {current_time}\n"
            message += f"📰 Найдено новостей о литературе: {news_count}\n"
            
            if news_count == 0:
                message += f"\n🔍 Сегодня актуальных новостей о литературе не найдено\\."
            else:
                message += f"\n✅ Все новости опубликованы в канале\\!"
            
            await self.bot.send_message(
                chat_id=self.channel_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN_V2
            )
            
            logger.info("Daily summary sent successfully")
            
        except Exception as e:
            logger.error(f"Failed to send daily summary: {str(e)}")

# Функция для тестирования
async def test_telegram_bot():
    try:
        bot = TelegramNewsBot()
        
        # Тестируем подключение
        if await bot.test_connection():
            print("✅ Telegram bot connection successful!")
            
            # Создаем тестовую новость
            test_news = NewsItem(
                title="Тестовая новость о литературе",
                description="Это тестовое описание новости для проверки работы бота.",
                url="https://example.com/test-news",
                published=datetime.now(),
                source="Test Source"
            )
            
            # Отправляем тестовую новость
            success = await bot.send_news_to_channel([test_news])
            if success:
                print("✅ Test news sent successfully!")
            else:
                print("❌ Failed to send test news")
        else:
            print("❌ Telegram bot connection failed!")
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_telegram_bot())