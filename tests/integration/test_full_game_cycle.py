from unittest.mock import patch

from ddd_fantasy_rpg.domain import Player, Race, PlayerClass, ExpeditionDistance, MonsterEncounter
from ddd_fantasy_rpg.infrastructure.random import SystemRandomProvider
from ddd_fantasy_rpg.infrastructure.time import UtcTimeProvider
from ddd_fantasy_rpg.infrastructure.repositories import (
    InMemoryPlayerRepository,
    InMemoryExpeditionRepository,
    InMemoryBattleRepository,
)
from ddd_fantasy_rpg.application import (
    StartExpeditionUseCase,
    CompleteExpeditionUseCase,
    StartBattleUseCase,
)


@patch("ddd_fantasy_rpg.domain.expedition.Expedition.is_finished", return_value=True)
async def test_full_game_cycle(mock_is_finished):
    # 1. Инициализация репозиториев
    player_repo = InMemoryPlayerRepository()
    exp_repo = InMemoryExpeditionRepository()
    battle_repo = InMemoryBattleRepository()
    
    randome_provider = SystemRandomProvider()
    time_provider = UtcTimeProvider()

    # 2. Создаём игрока
    player = Player("p1", 123, "Aragorn", Race.HUMAN, PlayerClass.WARRIOR)
    player_repo.save(player)

    # 3. Use Cases
    start_exp_uc = StartExpeditionUseCase(player_repo, exp_repo, time_provider)
    start_battle_uc = StartBattleUseCase(player_repo, battle_repo)
    complete_exp_uc = CompleteExpeditionUseCase(exp_repo, player_repo, start_battle_uc, time_provider, randome_provider)

    # 4. Игрок начинает вылазку
    await start_exp_uc.execute("p1", ExpeditionDistance.NEAR)

    # 5. Вылазка завершается → запускается бой
    event = complete_exp_uc.execute("p1")
    
    assert isinstance(event, MonsterEncounter), f"Expected MonsterEncounter, got {type(event)}"
    assert event.monster is not None

    # 6. Проверяем, что бой создан
    battle = battle_repo.get_active_battle_for_player("p1")
    assert battle is not None
    assert battle._attacker.name == "Aragorn"
    assert battle._defender.name == event.monster.name

    # 7. Игрок атакует
    from ddd_fantasy_rpg.domain.battle import BattleAction, BattleActionType
    result = battle.perform_action("p1", BattleAction(BattleActionType.ATTACK), randome_provider)
    assert result["success"] is True
    assert battle._defender.current_hp < battle._defender.stats.max_hp

    print("✅ Full game cycle passed!")