import uuid

from ddd_fantasy_rpg.domain.common.time_provider import TimeProvider
from ddd_fantasy_rpg.domain.common.unit_of_work import UnitOfWork

from ddd_fantasy_rpg.domain.player import PlayerNotFoundError, PlayerAlreadyOnExpeditionError
from ddd_fantasy_rpg.domain.expedition import Expedition, ExpeditionDistance
from ddd_fantasy_rpg.application.use_cases.generate_events import GenerateEventUseCase


class StartExpeditionUseCase:
    """
    Use Case для старта экспедиции.
    """
    def __init__(
        self,
        generate_event_use_case: GenerateEventUseCase,
        time_provider: TimeProvider,
    ):
        self._generate_event_uc = generate_event_use_case
        self._time_provider = time_provider
        
    
    async def execute(self, player_id: str, distance: ExpeditionDistance, uow: UnitOfWork):
        player = await uow.players.get_by_id(player_id)
        if player is None:
            raise PlayerNotFoundError(player_id)
        
        active_expedition = await uow.expeditions.get_by_player_id(player_id)
        if active_expedition and not active_expedition.is_finished(self._time_provider):
            raise PlayerAlreadyOnExpeditionError(player_id)
        
        event = await self._generate_event_uc.execute(distance)
        
        expedition_id = str(uuid.uuid4())
        
        expedition = Expedition.start_for(
            expedition_id=expedition_id,
            player_id=player_id,
            distance=distance,
            event=event,
            time_provider=self._time_provider
        )
        
        await uow.expeditions.save(expedition)