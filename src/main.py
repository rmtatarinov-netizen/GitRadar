import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from src.config import settings
from src.bot.handlers import start_handler, search_handler, new_handler, top_handler
from src.storage.repository import AsyncSessionLocal
from src.storage.models import init_db # This is a placeholder, will be in repository.py actually

# Fixing the import: init_db is in repository.py
from src.storage.repository import init_db

async def main():
    logging.basicConfig(level=settings.LOG_LEVEL)
    
    # Init DB
    await init_db()
    
    # Start Scheduler
    from src.scheduler.sync import start_scheduler
    await start_scheduler()
    
    # Loguru configuration
    from loguru import logger
    logger.add("logs/app.log", rotation="1 week", retention="1 month", level="INFO")
    
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    # Register handlers
    dp.message.register(start_handler, Command("start"))
    dp.message.register(lambda m, s=AsyncSessionLocal: search_handler(m, s), Command("search"))
    dp.message.register(lambda m, s=AsyncSessionLocal: new_handler(m, s), Command("new"))
    dp.message.register(lambda m, s=AsyncSessionLocal: top_handler(m, s), Command("top"))
    
    # Admin handlers
    from src.bot.admin import admin_edit_category, admin_delete_skill
    dp.message.register(lambda m, s=AsyncSessionLocal: admin_edit_category(m, s), Command("admin_cat"))
    dp.message.register(lambda m, s=AsyncSessionLocal: admin_delete_skill(m, s), Command("admin_del"))

    logging.info("Bot started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
