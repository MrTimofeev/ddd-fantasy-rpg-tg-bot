from unittest.mock import Mock
from ddd_fantasy_rpg.domain import Player, Race, PlayerClass, ExpeditionDistance
from ddd_fantasy_rpg.application import StartExpeditionUseCase


def test_start_expedition_success():
    player = Player("123", 987, "Hero", Race.HUMAN, PlayerClass.WARRIOR)
    player_repo = Mock()
    player_repo.get_by_id.return_value = player

    expedition_repo = Mock()
    expedition_repo.get_by_player_id.return_value = None  # нет активной вылазки

    use_case = StartExpeditionUseCase(player_repo, expedition_repo)

    expedition = use_case.execute("123", ExpeditionDistance.NEAR)

    assert expedition.player_id == "123"
    assert expedition.distance == ExpeditionDistance.NEAR
    expedition_repo.save.assert_called_once_with(expedition)


def test_start_expedition_fails_if_already_on_expedition():
    player = Player("123", 987, "Busy", Race.ELF, PlayerClass.MAGE)
    player_repo = Mock()
    player_repo.get_by_id.return_value = player

    active_expedition = Mock()
    active_expedition.is_finished.return_value = False
    expedition_repo = Mock()
    expedition_repo.get_by_player_id.return_value = active_expedition

    use_case = StartExpeditionUseCase(player_repo, expedition_repo)

    try:
        use_case.execute("123", ExpeditionDistance.FAR)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "already on an expedition" in str(e)
