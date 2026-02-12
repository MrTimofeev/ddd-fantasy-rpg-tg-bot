from datetime import datetime
from typing import Optional

from ddd_fantasy_rpg.domain.player import Player
from ddd_fantasy_rpg.domain.expedition import Expedition, ExpeditionDistance

from ddd_fantasy_rpg.domain.repositories.player_repository import PlayerRepository
from ddd_fantasy_rpg.domain.repositories.expedition_repository import ExpeditionRepository


class StartExpeditionUseCase:
    def __init__(
        self,
        player_repository: PlayerRepository,
        expedition_repository: ExpeditionRepository,
    ):
        self._player_repo = player_repository
        self._expedition_repo = expedition_repository
        
    
    def execute(self, player_id: str, distance: ExpeditionDistance) -> Expedition:
        player = self._player_repo.get_by_id(player_id)
        if player is None:
            raise ValueError(f"Player with ID {player_id} not found")
        
        active_expedition = self._expedition_repo.get_by_player_id(player_id)
        if active_expedition and not active_expedition.is_finished():
            raise ValueError("Player is already on an expedition")
        
        expedition = Expedition.start_for(player_id, distance)
        
        self._expedition_repo.save(expedition)
        
        return expedition