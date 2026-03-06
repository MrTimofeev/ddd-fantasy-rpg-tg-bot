from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ddd_fantasy_rpg.domain.player.player import Player
from ddd_fantasy_rpg.domain.repositories.player_repository import PlayerRepository
from ddd_fantasy_rpg.infrastructure.database.models import PlayerORM
from ddd_fantasy_rpg.infrastructure.database.mappers import player_to_orm, player_from_orm


class AsyncPlayerRepository(PlayerRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, player_id: str) -> Optional[Player]:
        query = (
            select(PlayerORM)
            .options(
                selectinload(PlayerORM.stats),
                selectinload(PlayerORM.items)
            )
            .where(PlayerORM.id == player_id)
        )

        result = await self._session.execute(query)
        orm = result.scalar_one_or_none()
        if not orm:
            return None

        return player_from_orm(orm)

    async def save(self, player: Player) -> None:
        orm = player_to_orm(player)
        await self._session.merge(orm)
