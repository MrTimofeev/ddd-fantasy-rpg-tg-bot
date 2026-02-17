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
    AsyncPlayerRepository,
    AsyncExpeditionRepository,
    AsyncBattleRepository,
)


def create_async_use_cases(session: AsyncSession):
    player_repo = AsyncPlayerRepository(session)
    exp_repo = AsyncExpeditionRepository(session)
    battle_repo = AsyncBattleRepository(session)

    time_provider = UtcTimeProvider()
    random_provider = SystemRandomProvider()

    start_battle_uc = StartBattleUseCase(player_repo, battle_repo)
    start_exp_uc = StartExpeditionUseCase(player_repo, exp_repo, time_provider)
    complete_exp_uc = CompleteExpeditionUseCase(
        exp_repo,
        player_repo,
        start_battle_uc,
        time_provider,
        random_provider
    )
    complete_battle_uc = CompleteBattleUseCase(player_repo, battle_repo, exp_repo)

    return {
        "start_expedition": start_exp_uc,
        "complete_expedition": complete_exp_uc,
        "start_battle": start_battle_uc,
        "complete_battle": complete_battle_uc,
        "player_repo": player_repo,
        "exp_repo": exp_repo,
        "battle_repo": battle_repo,
    }
