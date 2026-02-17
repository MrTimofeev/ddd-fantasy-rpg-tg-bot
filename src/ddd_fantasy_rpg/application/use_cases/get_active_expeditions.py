from typing import List

from ddd_fantasy_rpg.domain.expedition import Expedition
from ddd_fantasy_rpg.domain.repositories.expedition_repository import ExpeditionRepository


class GetActiveExpeditionUseCase:
    """
    Use Case для получение всех активных экспедиций.
    Используется в фоновых задачах.
    """
    
    def __init__(self, expedition_repository: ExpeditionRepository):
        self._expedition_repo = expedition_repository
        
    async def execute(self) -> List[Expedition]:
        """
        Возвращает все активные (не завершенные) экспедиции.
        """
        
        return await self._expedition_repo.get_all_active_expeditions()