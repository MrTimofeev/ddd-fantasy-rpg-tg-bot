from aiogram import Bot

from ddd_fantasy_rpg.infrastructure.notifications import TelegramNotificationService

from ddd_fantasy_rpg.bot.aiogram_bot.background_tasks import (
    ExpeditionCompletionBackgroundTask,
    PvpMatchingBackgroundTask
)

def create_background_task(bot: Bot, async_session_maker: callable):
    """Создает фоновые задачи"""
    notification_service = TelegramNotificationService(bot)
    
    expedition_task = ExpeditionCompletionBackgroundTask(
        notification_service=notification_service,
        async_session_maker=async_session_maker
    )
    
    pvp_task = PvpMatchingBackgroundTask(
        notification_service=notification_service,
        async_session_maker=async_session_maker
    )
    
    return {
        "expedition_completion": expedition_task,
        "pvp_matching": pvp_task,
    }