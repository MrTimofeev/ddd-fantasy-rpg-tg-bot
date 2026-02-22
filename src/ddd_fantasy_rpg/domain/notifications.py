from abc import ABC, abstractmethod
from typing import List

from ddd_fantasy_rpg.application.use_cases.match_pvp_expeditions import PvpMatchResult
from ddd_fantasy_rpg.application.use_cases.perform_battle_action import BattleActionResult

class NotificationService(ABC):
    """Абстракция сервиса уведомлений."""
    
    @abstractmethod
    async def notify_expedition_complete(
        self,
        player_id: str,
        monster_name: str,
        monster_level: int
    ) -> None:
        """Уведомляет игрока о завершении экспедиции с мотрстром."""
        raise NotImplementedError
    
    @abstractmethod
    async def notify_pvp_match_found(
        self,
        matches: List[PvpMatchResult]
    ) -> None:
        """Уведомляет о найденых PVP дуэлях."""
        raise NotImplementedError
    
    @abstractmethod
    async def notify_battle_turn(
        self,
        player_id: str,
        battle_state: str,
    ) -> None:
        """Уведомляет игрока о его ходе в бою."""
        raise NotImplementedError
    
    @abstractmethod
    async def notify_battle_action_result(
        self,
        player_id: str,
        result: BattleActionResult,
        is_current_player: bool = True
    ) -> None:
        """Уведомляет игрока о результате действия в бою."""
        raise NotImplementedError
        
    @abstractmethod
    async def notify_battle_finished(
        self,
        winner_id: str,
        loser_id: str,
        battle_outcone: dict
    ) -> None:
        """Уведомляет игроков о завершении боя."""
        raise NotImplementedError
    