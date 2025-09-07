#!/usr/bin/env python3
"""
Литературный новостной бот для Telegram
Автоматически находит и публикует новости о литературе в Telegram канал
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime, timedelta
from typing import Optional
import schedule
import time
from threading import Thread

from config import UPDATE_INTERVAL_HOURS
from news_scraper import LiteratureNewsScraper
from telegram_bot import TelegramNewsBot

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('literature_bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class LiteratureNewsBot:
    def __init__(self):
        self.news_scraper = LiteratureNewsScraper()
        self.telegram_bot = TelegramNewsBot()
        self.is_running = False
        self.last_update = None
        
    async def initialize(self) -> bool:
        """Инициализация бота"""
        try:
            logger.info("Initializing Literature News Bot...")
            
            # Тестируем подключение к Telegram
            if not await self.telegram_bot.test_connection():
                logger.error("Failed to connect to Telegram. Check your bot token and channel ID.")
                return False
            
            logger.info("Bot initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {str(e)}")
            return False
    
    async def update_news(self):
        """Основная функция обновления новостей"""
        try:
            logger.info("Starting news update...")
            
            # Получаем новости
            news_items = await self.news_scraper.get_latest_literature_news()
            logger.info(f"Found {len(news_items)} new literature news items")
            
            if news_items:
                # Отправляем новости в канал
                success = await self.telegram_bot.send_news_to_channel(news_items)
                
                if success:
                    # Отмечаем новости как отправленные
                    self.news_scraper.mark_news_as_sent(news_items)
                    logger.info(f"Successfully sent {len(news_items)} news items to channel")
                else:
                    logger.warning("Some news items failed to send")
            else:
                logger.info("No new literature news found")
            
            # Отправляем ежедневную сводку (только один раз в день)
            now = datetime.now()
            if (not self.last_update or 
                self.last_update.date() != now.date()):
                await self.telegram_bot.send_daily_summary(len(news_items))
            
            self.last_update = now
            logger.info("News update completed successfully")
            
        except Exception as e:
            logger.error(f"Error during news update: {str(e)}")
            try:
                await self.telegram_bot.send_status_message(
                    f"❌ Ошибка при обновлении новостей: {str(e)}"
                )
            except:
                pass
    
    async def run_update_cycle(self):
        """Запускает один цикл обновления новостей"""
        try:
            await self.update_news()
        except Exception as e:
            logger.error(f"Error in update cycle: {str(e)}")
        finally:
            # Закрываем сессию scraper'а после каждого цикла
            await self.news_scraper.close_session()
    
    def schedule_updates(self):
        """Настраивает расписание обновлений"""
        # Запускаем обновления каждые N часов
        schedule.every(UPDATE_INTERVAL_HOURS).hours.do(
            lambda: asyncio.create_task(self.run_update_cycle())
        )
        
        # Дополнительно запускаем в определенное время дня
        schedule.every().day.at("09:00").do(
            lambda: asyncio.create_task(self.run_update_cycle())
        )
        schedule.every().day.at("15:00").do(
            lambda: asyncio.create_task(self.run_update_cycle())
        )
        schedule.every().day.at("21:00").do(
            lambda: asyncio.create_task(self.run_update_cycle())
        )
        
        logger.info(f"Scheduled updates every {UPDATE_INTERVAL_HOURS} hours and at 09:00, 15:00, 21:00")
    
    def run_scheduler(self):
        """Запускает планировщик в отдельном потоке"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Проверяем каждую минуту
    
    async def start(self):
        """Запускает бота"""
        try:
            # Инициализируем бота
            if not await self.initialize():
                return False
            
            self.is_running = True
            
            # Отправляем уведомление о запуске
            await self.telegram_bot.send_status_message(
                f"🚀 Бот запущен\\!\n\n"
                f"📅 Время запуска: {datetime.now().strftime('%d\\.%m\\.%Y %H:%M:%S')}\n"
                f"⏰ Интервал обновлений: каждые {UPDATE_INTERVAL_HOURS} часов\n"
                f"📰 Источники: RSS каналы и News API"
            )
            
            # Настраиваем расписание
            self.schedule_updates()
            
            # Запускаем первое обновление сразу
            logger.info("Running initial news update...")
            await self.run_update_cycle()
            
            # Запускаем планировщик в отдельном потоке
            scheduler_thread = Thread(target=self.run_scheduler, daemon=True)
            scheduler_thread.start()
            
            logger.info("Bot started successfully! Press Ctrl+C to stop.")
            
            # Основной цикл
            while self.is_running:
                await asyncio.sleep(1)
            
            return True
            
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, stopping bot...")
            await self.stop()
        except Exception as e:
            logger.error(f"Error starting bot: {str(e)}")
            return False
    
    async def stop(self):
        """Останавливает бота"""
        try:
            logger.info("Stopping Literature News Bot...")
            self.is_running = False
            
            # Закрываем сессию scraper'а
            await self.news_scraper.close_session()
            
            # Отправляем уведомление об остановке
            await self.telegram_bot.send_status_message(
                f"🛑 Бот остановлен\n\n"
                f"📅 Время остановки: {datetime.now().strftime('%d\\.%m\\.%Y %H:%M:%S')}"
            )
            
            logger.info("Bot stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping bot: {str(e)}")

def signal_handler(signum, frame):
    """Обработчик сигналов для корректного завершения"""
    logger.info(f"Received signal {signum}, initiating shutdown...")
    # Здесь мы не можем вызвать async функцию напрямую
    # Поэтому просто устанавливаем флаг остановки
    sys.exit(0)

async def main():
    """Главная функция"""
    # Настраиваем обработчики сигналов
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Создаем и запускаем бота
    bot = LiteratureNewsBot()
    
    try:
        success = await bot.start()
        if not success:
            logger.error("Failed to start bot")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)
    finally:
        await bot.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)