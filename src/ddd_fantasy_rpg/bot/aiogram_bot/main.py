import asyncio
import logging
import os
from dotenv import load_dotenv
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from ddd_fantasy_rpg.bot.aiogram_bot.handlers import register_all_handlers
from ddd_fantasy_rpg.infrastructure.database.async_session import get_async_sessionmaker
from ddd_fantasy_rpg.infrastructure.repositories.item_template_repository import ItemTemplateRepository
from ddd_fantasy_rpg.infrastructure.repositories.skill_template_repository import SkillTemplateRepository
from ddd_fantasy_rpg.application.factories import ApplicationFactory


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

    # Инициализируем предметы
    # TODO: вынести в фабрику
    config_dir = Path(__file__).parent.parent.parent / "config"
    print(config_dir)
    ItemTemplateRepository.initialize(config_dir)
    SkillTemplateRepository.initialized(config_dir)
    
    # Создаем фабрику и получаем единый контекст
    app_factory = ApplicationFactory(bot, async_session_maker)
    dependencies = app_factory.create_dependency_context()

    # Передаем зависимости
    dp["dependencies"] = dependencies

    # Запуск фоновых задач
    background_tasks = app_factory.create_background_tasks()
    asyncio.create_task(background_tasks["complete_expetidion_by_time"].run())
    asyncio.create_task(background_tasks["start_event_for_complete_expeditions"].run())
    asyncio.create_task(background_tasks["pvp_matching"].run())

    register_all_handlers(dp, dependencies)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
