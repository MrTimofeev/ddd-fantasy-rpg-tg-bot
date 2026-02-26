from ddd_fantasy_rpg.domain.common.unit_of_work import UnitOfWork
from ddd_fantasy_rpg.domain.common.time_provider import TimeProvider
from ddd_fantasy_rpg.domain.expedition import ExpeditionNotFoundError, ExpeditionNotFinishedError

class CompleteExpeditionByTimeUseCase:
    """Use case для завершения экспедиций по времени"""
    
    def __init__(
        self,
        time_provider: TimeProvider,
    ):
        self._time_provider = time_provider
       
    async def execute(self, player_id, uow: UnitOfWork):
        # 1. Получаем активную вылазку
        expedition = await uow.expeditions.get_by_player_id(player_id)
        if not expedition:
            raise ExpeditionNotFoundError(player_id)
        if not expedition.is_finished(self._time_provider):
            raise ExpeditionNotFinishedError()
            
        expedition.complete()
        
        await uow.expeditions.save(expedition)

