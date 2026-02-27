from abc import ABC, abstractmethod

from ddd_fantasy_rpg.domain.battle.battle_result import BattleResult
from ddd_fantasy_rpg.domain.player import Player


class NotificationService(ABC):
    """Абстракция сервиса уведомлений."""
    
    @abstractmethod
    async def notify_expedition_complete(
        self,
        player_id: str,
        player_hp: int,
        monster_name: str,
        monster_level: int,
        monster_hp: int
    ) -> None:
        """Уведомляет игрока о завершении экспедиции с мотрстром."""
        raise NotImplementedError
    
    @abstractmethod
    async def notify_pvp_match_found(
        self,
        player1: Player,
        player2: Player,
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
        result,
        is_current_player: bool = True,
    ) -> None:
        """Уведомляет игрока о результате действия в бою."""
        raise NotImplementedError
        
    @abstractmethod
    async def notify_battle_finished(
        self,
        battle_result: BattleResult,
    ) -> None:
        """Уведомляет игроков о завершении боя."""
        raise NotImplementedError
    