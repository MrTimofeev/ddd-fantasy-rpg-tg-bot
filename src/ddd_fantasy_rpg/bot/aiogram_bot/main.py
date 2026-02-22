import asyncio
import logging
import os
from dotenv import load_dotenv


from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from ddd_fantasy_rpg.bot.aiogram_bot.handlers import register_handlers
from ddd_fantasy_rpg.infrastructure.database.async_session import get_async_sessionmaker
from ddd_fantasy_rpg.application.async_factories import ApplicationFactory


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
    
    app_factory = ApplicationFactory(bot, async_session_maker)
    background_tasks = app_factory.create_background_tasks()
    use_cases = app_factory.get_use_cases()
    serivices = app_factory.get_services()
    
    # Передаем сессию и use_case в middleware
    dp["async_session_maker"] = async_session_maker

    dp["create_plyaer_use_case"] = use_cases["create_player"]
    dp["start_expedition_use_case"] = use_cases["start_expedition"]
    dp["perform_battle_action_use_case"] = use_cases["perform_battle_action"]
    
    dp["notification_service"] = serivices["notification_service"]

    
    register_handlers(dp)

    # Запуск фоновой задачи
    asyncio.create_task(background_tasks["expedition_completion"].run())
    asyncio.create_task(background_tasks["pvp_matching"].run())

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
