import asyncio
import logging
import os
from dotenv import load_dotenv


from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from ddd_fantasy_rpg.bot.aiogram_bot.handlers import register_handlers
from ddd_fantasy_rpg.infrastructure.database.async_session import get_async_sessionmaker
from ddd_fantasy_rpg.bot.aiogram_bot.background_tasks import check_completed_expeditions


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():

    load_dotenv()
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError(
            "TELEGRAM_BOT_TOKEN is required! Check your .env file.")

    async_session_maker, init_db = get_async_sessionmaker()

    await init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(
        parse_mode=ParseMode.HTML))

    dp = Dispatcher()

    # Передаем сессию в middleware
    dp["async_session_maker"] = async_session_maker

    register_handlers(dp)

    # Запуск фоновой задачи
    asyncio.create_task(check_completed_expeditions(bot, async_session_maker))

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
