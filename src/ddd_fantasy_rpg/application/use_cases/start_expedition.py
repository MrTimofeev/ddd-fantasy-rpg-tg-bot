from ddd_fantasy_rpg.domain.common.time_provider import TimeProvider
from ddd_fantasy_rpg.domain.common.unit_of_work import UnitOfWork

from ddd_fantasy_rpg.domain.common.exceptions import PlayerNotFoundError, PlayerAlreadyOnExpeditionError
from ddd_fantasy_rpg.domain.expedition import Expedition, ExpeditionDistance


class StartExpeditionUseCase:
    """
    Use Case для старта экспедиции.
    """
    def __init__(
        self,
        time_provider: TimeProvider,
    ):
        self._time_provider = time_provider
        
    
    async def execute(self, player_id: str, distance: ExpeditionDistance, uow: UnitOfWork) -> Expedition:
        player = await uow.players.get_by_id(player_id)
        if player is None:
            raise PlayerNotFoundError(player_id)
        
        active_expedition = await uow.expeditions.get_by_player_id(player_id)
        if active_expedition and not active_expedition.is_finished(self._time_provider):
            raise PlayerAlreadyOnExpeditionError(player_id)
        
        expedition = Expedition.start_for(
            player_id=player_id,
            distance=distance,
            time_provider=self._time_provider
        )
        
        await uow.expeditions.save(expedition)
        
        return expedition