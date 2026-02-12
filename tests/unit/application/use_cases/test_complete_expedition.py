import random
from unittest.mock import Mock

from ddd_fantasy_rpg.domain.player import Player, Race, PlayerClass
from ddd_fantasy_rpg.domain.expedition import ExpeditionDistance, Expedition, MonsterEncounter
from ddd_fantasy_rpg.application.use_cases.complete_expedition import CompleteExpeditionUseCase
from ddd_fantasy_rpg.application.use_cases.start_battle import StartBattleUseCase


def test_complete_expedition_starts_battle():
    random.seed(42)

    # Создаём вылазку и сразу "завершаем" её
    expedition = Expedition.start_for("p1", ExpeditionDistance.NEAR)
    expedition.end_time = expedition.start_time  # теперь is_finished() == True

    expedition_repo = Mock()
    expedition_repo.get_by_player_id.return_value = expedition

    player_repo = Mock()
    player_repo.get_by_id.return_value = Player(
        "p1", 123, "Hero", Race.HUMAN, PlayerClass.WARRIOR
    )

    battle_uc = Mock(spec=StartBattleUseCase)

    use_case = CompleteExpeditionUseCase(
        expedition_repo, player_repo, battle_uc)

    result = use_case.execute("p1")

    assert isinstance(result, MonsterEncounter)
    assert result.monster.name in ["Goblin", "Orc"]
    battle_uc.execute.assert_called_once_with("p1", result.monster)
    assert expedition.outcome == result
    expedition_repo.save.assert_called_once_with(expedition)
