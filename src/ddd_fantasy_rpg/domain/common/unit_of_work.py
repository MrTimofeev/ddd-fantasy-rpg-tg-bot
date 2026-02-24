from abc import ABC, abstractmethod
from typing import AsyncContextManager

from ddd_fantasy_rpg.domain.repositories.player_repository import PlayerRepository
from ddd_fantasy_rpg.domain.repositories.expedition_repository import ExpeditionRepository
from ddd_fantasy_rpg.domain.repositories.battle_repository import BattleRepository


class UnitOfWork(ABC):
    """Абстракция для Unit Of Work для упрвления транзакциями."""
    
    players: PlayerRepository
    expeditions: ExpeditionRepository
    battles: BattleRepository
    
    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork":
        raise NotImplementedError
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def commit(self) -> None:
        """Подтверждает транзакцию."""
        raise NotImplementedError
    
    @abstractmethod
    async def rollback(self) -> None:
        """Откатывает транзакцию."""
        raise NotImplementedError