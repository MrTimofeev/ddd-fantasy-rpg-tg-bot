from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ddd_fantasy_rpg.domain.player import Player

class PlayerRepository(ABC):
    @abstractmethod
    async def get_by_id(self, player_id: str) -> Optional["Player"]:
        raise NotImplementedError
    
    @abstractmethod
    async def save(self, player: "Player") -> None:
        raise NotImplementedError