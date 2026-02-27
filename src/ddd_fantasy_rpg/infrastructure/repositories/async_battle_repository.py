from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ddd_fantasy_rpg.domain.battle import Battle
from ddd_fantasy_rpg.domain.repositories.battle_repository import BattleRepository
from ddd_fantasy_rpg.infrastructure.database.models import BattleORM
from ddd_fantasy_rpg.infrastructure.database.mappers import battle_to_orm, battle_from_orm


class AsyncBattleRepository(BattleRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, battle: Battle) -> None:
        orm = battle_to_orm(battle)
        await self._session.merge(orm)

    async def get_by_id(self, battle_id: str) -> Optional[Battle]:
        result = await self._session.execute(select(BattleORM).where(BattleORM.id == battle_id))
        orm = result.scalar_one_or_none()
        return battle_from_orm(orm) if orm else None

    async def get_active_battle_for_player(self, player_id: str) -> Optional[Battle]:
        result = await self._session.execute(
            select(BattleORM).where(
                ((BattleORM.attacker_id == player_id) |
                 (BattleORM.defender_id == player_id)),
                BattleORM.is_finished == False
            )
        )
        orm = result.scalar_one_or_none()
        return battle_from_orm(orm) if orm else None
