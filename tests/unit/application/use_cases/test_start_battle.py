from unittest.mock import Mock
from ddd_fantasy_rpg.domain import Player, Race, PlayerClass, Monster
from ddd_fantasy_rpg.application import StartBattleUseCase


def test_start_battle_with_monster():
    player = Player("p1", 123, "Hero", Race.HUMAN, PlayerClass.WARRIOR)
    monster = Monster("m1", "Goblin", level=3, base_damage=5, max_hp=30, drop_items=[], flee_difficulty=30)

    player_repo = Mock()
    player_repo.get_by_id.return_value = player

    battle_repo = Mock()
    battle_repo.get_active_battle_for_player.return_value = None

    use_case = StartBattleUseCase(player_repo, battle_repo)

    battle = use_case.start_pve_battle("p1", monster)

    assert battle._attacker.name == "Hero"
    assert battle._defender.name == "Goblin"
    assert len(battle._attacker.skills) > 0  # у воина есть скиллы
    battle_repo.save.assert_called_once()