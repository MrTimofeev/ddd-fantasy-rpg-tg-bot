from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ddd_fantasy_rpg.domain.expedition import Expedition


class ExpeditionRepository(ABC):
    @abstractmethod
    async def save(self, expedition: "Expedition") -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_player_id(self, player_id: str) -> Optional["Expedition"]:
        raise NotImplementedError
    
    @abstractmethod
    async def get_all_active_expeditions(self) -> list["Expedition"]:
        raise NotImplementedError
    
    @abstractmethod
    async def get_completed_but_unprocessed_expeditions(self) -> list["Expedition"]:
        raise NotImplementedError