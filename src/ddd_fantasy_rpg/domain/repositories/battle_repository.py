from abc import ABC, abstractmethod
from typing import Optional

from ..battle import Battle

class BattleRepository(ABC):
    @abstractmethod
    async def save(self, battle: Battle) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_id(self, battle_id: str) -> Optional[Battle]:
        raise NotImplementedError
    
    @abstractmethod
    async def get_active_battle_for_player(self, player_id: str) -> Optional[Battle]:
        raise NotImplementedError