from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ddd_fantasy_rpg.domain import Player
from ddd_fantasy_rpg.domain.repositories.player_repository import PlayerRepository
from ddd_fantasy_rpg.infrastructure.database.models import PlayerORM
from ddd_fantasy_rpg.infrastructure.database.mappers import player_to_orm, player_from_orm


class AsyncSqlitePlayerRepository(PlayerRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, player_id: str) -> Optional[Player]:
        result = await self._session.execute(select(PlayerORM).where(PlayerORM.id == player_id))
        orm = result.scalar_one_or_none()
        return player_from_orm(orm) if orm else None

    async def save(self, player: Player) -> None:
        orm = player_to_orm(player)
        existing = await self.get_by_id(player.id)

        if existing:
            merged = await self._session.merge(orm)
            await self._session.commit()
        else:
            self._session.add(orm)
            await self._session.commit()
