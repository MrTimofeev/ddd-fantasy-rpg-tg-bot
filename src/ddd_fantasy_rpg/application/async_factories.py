from sqlalchemy.ext.asyncio import AsyncSession
from ddd_fantasy_rpg.infrastructure.time import UtcTimeProvider
from ddd_fantasy_rpg.infrastructure.random import SystemRandomProvider
from ddd_fantasy_rpg.application import (
    StartExpeditionUseCase,
    StartBattleUseCase,
    CompleteExpeditionUseCase,
    CompleteBattleUseCase,
    GetActiveExpeditionUseCase,
    MatchPvpExpeditionsUseCase,
    PerformBattleActionUseCase,
    CreatePlayerUseCase,
)


def create_async_use_cases():
    time_provider = UtcTimeProvider()
    random_provider = SystemRandomProvider()

    start_battle_uc = StartBattleUseCase()
    start_exp_uc = StartExpeditionUseCase( time_provider)
    complete_exp_uc = CompleteExpeditionUseCase(
        start_battle_uc,
        time_provider,
        random_provider
    )
    complete_battle_uc = CompleteBattleUseCase()
    get_active_exp_uc = GetActiveExpeditionUseCase()
    match_pvp_uc = MatchPvpExpeditionsUseCase(start_battle_uc)
    perform_battle_action_uc = PerformBattleActionUseCase(random_provider, complete_battle_uc)
    create_player_uc = CreatePlayerUseCase()

    return {
        "start_expedition": start_exp_uc,
        "complete_expedition": complete_exp_uc,
        "start_battle": start_battle_uc,
        "complete_battle": complete_battle_uc,
        "get_active_expeditions": get_active_exp_uc,
        "match_pvp_expeditions": match_pvp_uc,
        "perform_battle_action": perform_battle_action_uc,
        "create_player": create_player_uc,
    }
