from typing import Optional, Dict

from ddd_fantasy_rpg.domain.player import Player
from ddd_fantasy_rpg.domain.repositories.player_repository import PlayerRepository

class InMemoryPlayerRepository(PlayerRepository):
    def __init__(self):
        self._players: Dict[str, Player] = {}
        
    def get_by_id(self, player_id: str) -> Optional[Player]:
        return self._players.get(player_id)

    def save(self, player: Player) -> None:
        self._players[player.id] = player