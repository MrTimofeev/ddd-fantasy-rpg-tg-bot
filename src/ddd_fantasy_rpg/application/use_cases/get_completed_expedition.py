from typing import List, Callable

from ddd_fantasy_rpg.domain.expedition.expedition import Expedition
from ddd_fantasy_rpg.domain.common.unit_of_work import UnitOfWork

class GetCompletedExpeditionUseCase:
    """
    Use Case для получение всех завершенных экспедиций.
    Используется в фоновых задачах.
    """
    
    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],

    ):
        self._uow_factory = uow_factory
    
    async def execute(self) -> List[Expedition]:
        """
        Возвращает все завершенные экспедиции.
        """
        async with self._uow_factory() as uow:   
            return await uow.expeditions.get_completed_expedition()