from sqlalchemy.ext.asyncio import AsyncSession

from ddd_fantasy_rpg.domain.common.unit_of_work import UnitOfWork
from ddd_fantasy_rpg.infrastructure.repositories import (
    AsyncPlayerRepository,
    AsyncExpeditionRepository,
    AsyncBattleRepository,
)


class SqlAlchemyUnitOfWork(UnitOfWork):
    """Реализация Unit of Work для SQLAlchemy."""
    
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session: AsyncSession = None
        
    
    async def __aenter__(self):
        self.session = self.session_factory()
        
        # Создаем репозитории с общей ссесией
        self.players = AsyncPlayerRepository(self.session)
        self.expeditions = AsyncExpeditionRepository(self.session)
        self.battles = AsyncBattleRepository(self.session)
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Произошла ошибка - откатываем 
            await self.rollback()
        else:
            # Успешно - коммитим
            await self.commit()
        
        await self.session.close()
        
    async def commit(self) -> None:
        await self.session.commit()
        
    async def rollback(self) -> None:
        await self.session.rollback()
    
        