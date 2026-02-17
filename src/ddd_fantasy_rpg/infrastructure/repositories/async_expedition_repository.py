from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ddd_fantasy_rpg.domain import Expedition
from ddd_fantasy_rpg.domain.repositories.expedition_repository import ExpeditionRepository
from ddd_fantasy_rpg.infrastructure.database.models import ExpeditionORM
from ddd_fantasy_rpg.infrastructure.database.mappers import expedition_to_orm, expedition_from_orm


class AsyncExpeditionRepository(ExpeditionRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, expedition: Expedition) -> None:
        orm = expedition_to_orm(expedition)
        merged = await self._session.merge(orm)
        await self._session.commit()

    async def get_by_player_id(self, player_id: str) -> Optional[Expedition]:
        result = await self._session.execute(
            select(ExpeditionORM).where(ExpeditionORM.player_id == player_id)
        )

        orm = result.scalar_one_or_none()
        return expedition_from_orm(orm) if orm else None

    async def get_all_active_expeditions(self) -> list[Expedition]:
        """
        Возвращаем все вылазки, которые:
        - завершились по веремени (end_time <= now),
        - еще не обработаны (outcome_type IS NULL).
        """
        now = datetime.now(timezone.utc)
        stmt = select(ExpeditionORM).where(
            and_(
                ExpeditionORM.end_time <= now,
                ExpeditionORM.outcome_type.is_(None),
                ExpeditionORM.status == "active"
            )
        )
        result = await self._session.execute(stmt)
        orm_objects = result.scalars().all()


        return [expedition_from_orm(orm) for orm in orm_objects]
    
    async def get_active_expeditions(self) -> list[Exception]:
        stmt = select(ExpeditionORM).where(ExpeditionORM.status == "active")
        result = await self._session.execute(stmt)
        orm_object = result.scalars().all()
        
        return [expedition_from_orm(orm) for orm in orm_object if orm]
    
    
        
        
