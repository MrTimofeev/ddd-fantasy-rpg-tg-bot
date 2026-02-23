from aiogram import Dispatcher
from ..dependency_context import DependencyContext


def register_all_handlers(dp: Dispatcher, dependencies: DependencyContext):
    """Регистрирует все хендлеры"""
    from . import battle_handler, player_handler, expedition_handler, start_handler
    
    start_handler.router.dependencies = dependencies
    player_handler.router.dependencies = dependencies
    expedition_handler.router.dependencies = dependencies
    battle_handler.router.dependencies = dependencies

    dp.include_router(start_handler.router)
    dp.include_router(player_handler.router)
    dp.include_router(expedition_handler.router)
    dp.include_router(battle_handler.router)
