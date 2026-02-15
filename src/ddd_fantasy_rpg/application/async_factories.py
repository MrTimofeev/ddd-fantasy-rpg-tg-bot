from sqlalchemy.ext.asyncio import AsyncSession
from ddd_fantasy_rpg.infrastructure.time import UtcTimeProvider
from ddd_fantasy_rpg.infrastructure.random import SystemRandomProvider
from ddd_fantasy_rpg.application import (
    StartExpeditionUseCase,
    StartBattleUseCase,
    CompleteExpeditionUseCase,
    CompleteBattleUseCase,
)
from ddd_fantasy_rpg.infrastructure.repositories import (
    AsyncSqlitePlayerRepository,
    AsyncSqliteExpeditionRepository,
    AsyncSqliteBattleRepository,
)


def create_async_use_cases(session: AsyncSession):
    player_repo = AsyncSqlitePlayerRepository(session)
    exp_repo = AsyncSqliteExpeditionRepository(session)
    battle_repo = AsyncSqliteBattleRepository(session)

    time_provider = UtcTimeProvider()
    randome_provider = SystemRandomProvider()

    start_battle_uc = StartBattleUseCase(player_repo, battle_repo)
    start_exp_uc = StartExpeditionUseCase(player_repo, exp_repo, time_provider)
    complete_exp_uc = CompleteExpeditionUseCase(
        exp_repo,
        player_repo,
        start_battle_uc,
        time_provider,
        randome_provider
    )
    complete_battle_uc = CompleteBattleUseCase(player_repo, battle_repo)

    return {
        "start_expedition": start_exp_uc,
        "complete_expedition": complete_exp_uc,
        "start_battle": start_battle_uc,
        "complete_battle": complete_battle_uc,
    }
