from dataclasses import dataclass
from typing import Callable

from ddd_fantasy_rpg.application import (
    CreatePlayerUseCase,
    StartExpeditionUseCase,
    PerformBattleActionUseCase
)
from ddd_fantasy_rpg.domain.notifications import NotificationService

@dataclass
class DependencyContext:
    """Контекст всех зависимостей для бота."""
    
    # Use Case
    create_player_use_case: CreatePlayerUseCase
    start_expedition_use_case: StartExpeditionUseCase
    perform_battle_action_use_case: PerformBattleActionUseCase
    
    # Services
    notification_service: NotificationService
    
    # Infrastructure
    async_session_maker: Callable