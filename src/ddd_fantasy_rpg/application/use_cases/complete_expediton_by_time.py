from typing import Callable

from ddd_fantasy_rpg.domain.common.unit_of_work import UnitOfWork
from ddd_fantasy_rpg.domain.common.time_provider import TimeProvider
from ddd_fantasy_rpg.application.events.dispatcher import EventDispatcher
from ddd_fantasy_rpg.domain.expedition.exceptions import ExpeditionNotFoundError, ExpeditionNotFinishedError

class CompleteExpeditionByTimeUseCase:
    """Use case для завершения экспедиций по времени"""
    
    def __init__(
        self,
        time_provider: TimeProvider,
        uow_factory: Callable[[], UnitOfWork],
        dispatcher: EventDispatcher,

    ):
        self._time_provider = time_provider
        self._uow_factory = uow_factory
        self._dispatcher = dispatcher
       
    async def execute(self, player_id):
        async with self._uow_factory() as uow:
            expedition = await uow.expeditions.get_by_player_id(player_id)
            if not expedition:
                raise ExpeditionNotFoundError(player_id)
            if not expedition.is_finished(self._time_provider.now()):
                raise ExpeditionNotFinishedError()
                
            expedition.complete_travel()
            
            await uow.expeditions.save(expedition)
            
            events_to_publish = expedition.pop_pending_events()
        
        if events_to_publish:
            await self._dispatcher.publish(events_to_publish)
        
        return expedition
            

