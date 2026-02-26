from dataclasses import dataclass
from typing import Callable, AsyncContextManager

from ddd_fantasy_rpg.application import (
    CreatePlayerUseCase,
    StartExpeditionUseCase,
    PerformBattleActionUseCase
)
from ddd_fantasy_rpg.application.formatters.battle_formatter import BattleMessageFormatter
from ddd_fantasy_rpg.domain.common.notifications import NotificationService
from ddd_fantasy_rpg.domain.common.unit_of_work import UnitOfWork


@dataclass
class DependencyContext:
    """Контекст всех зависимостей для бота."""

    # Use Case
    create_player_use_case: CreatePlayerUseCase
    start_expedition_use_case: StartExpeditionUseCase
    perform_battle_action_use_case: PerformBattleActionUseCase

    # Services
    notification_service: NotificationService
    message_formatter: BattleMessageFormatter

    unit_of_work_factory: Callable[[], UnitOfWork]

    def unit_of_work(self):
        """Фабричный метод создания Unif of Work."""
        return self.unit_of_work_factory()
