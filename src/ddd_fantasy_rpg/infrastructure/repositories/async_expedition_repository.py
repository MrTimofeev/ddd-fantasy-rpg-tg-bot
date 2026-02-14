from typing import Any, Optional
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ddd_fantasy_rpg.domain import Expedition, ExpeditionDistance
from ddd_fantasy_rpg.domain.repositories.expedition_repository import ExpeditionRepository
from ddd_fantasy_rpg.infrastructure.database.models import ExpeditionORM
from ddd_fantasy_rpg.infrastructure.database.mappers import expedition_to_orm, expedition_from_orm


class AsyncSqliteExpeditionRepository(ExpeditionRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, expedition: Expedition) -> None:
        orm = expedition_to_orm(expedition)
        existing = await self.get_by_player_id(expedition.player_id)
        if existing:
            merged = await self._session.merge(orm)
            await self._session.commit()
        else:
            self._session.add(orm)
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
        stmt = text("""
            SELECT player_id, distance, start_time, end_time, outcome_type, outcome_data
            FROM expeditions
            WHERE end_time <= :now AND outcome_type IS NULL
        """)
        result = await self._session.execute(stmt, {"now": now})
        rows = result.fetchall()
        
        expeditions = []
        for row in rows:
            player_id, distance_key, start_time, end_time, outcome_type, outcome_data = row
            
            # Воссоздаем объект Expedition без outcome (он None)
            distance = next(d for d in ExpeditionDistance if d.key == distance_key)
            expedition = Expedition(
                player_id=player_id,
                distance=distance,
                start_time=start_time,
                end_time=end_time, 
                outcome=None
            )
            expeditions.append(expedition)
        
        return expeditions
            