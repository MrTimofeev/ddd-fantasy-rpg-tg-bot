from abc import ABC, abstractmethod
from typing import Optional

from ..expedition import Expedition

class ExpeditionRepository(ABC):
    @abstractmethod
    async def save(self, expedition: Expedition) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_player_id(self, player_id: str) -> Optional[Expedition]:
        raise NotImplementedError
    
    @abstractmethod
    async def get_active_expeditions(self) -> list[Exception]:
        raise NotImplementedError