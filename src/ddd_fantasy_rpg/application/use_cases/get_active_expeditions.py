from typing import List

from ddd_fantasy_rpg.domain.expedition import Expedition
from ddd_fantasy_rpg.domain.unit_of_work import UnitOfWork

class GetActiveExpeditionUseCase:
    """
    Use Case для получение всех активных экспедиций.
    Используется в фоновых задачах.
    """
    
   
        
    async def execute(self, uow: UnitOfWork) -> List[Expedition]:
        """
        Возвращает все активные (не завершенные) экспедиции.
        """
        
        return await uow.expeditions.get_completed_but_unprocessed_expeditions()