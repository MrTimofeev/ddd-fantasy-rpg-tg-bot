from typing import List

from ddd_fantasy_rpg.domain.expedition import Expedition
from ddd_fantasy_rpg.domain.common.unit_of_work import UnitOfWork

class GetCompletedExpeditionUseCase:
    """
    Use Case для получение всех завершенных экспедиций.
    Используется в фоновых задачах.
    """
    
    async def execute(self, uow: UnitOfWork) -> List[Expedition]:
        """
        Возвращает все завершенные экспедиции.
        """
        
        return await uow.expeditions.get_completed_expedition()