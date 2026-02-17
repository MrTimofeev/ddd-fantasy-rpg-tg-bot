from typing import Optional, Dict

from ddd_fantasy_rpg.domain.expedition import Expedition
from ddd_fantasy_rpg.domain.repositories.expedition_repository import ExpeditionRepository


class InMemoryExpeditionRepository(ExpeditionRepository):
    def __init__(self):
        self._expeditions: Dict[str, Expedition] = {}
        
    def save(self, expedition: Expedition) -> None:
        self._expeditions[expedition.player_id] = expedition
        
    def get_by_player_id(self, player_id: str) -> Optional[Expedition]:
        return self._expeditions.get(player_id)
    
    