from abc import ABC, abstractmethod
from typing import Optional

from ..player import Player

class PlayerRepository(ABC):
    @abstractmethod
    async def get_by_id(self, player_id: str) -> Optional[Player]:
        raise NotImplementedError
    
    @abstractmethod
    async def save(self, player: Player) -> None:
        raise NotImplementedError