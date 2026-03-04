from ddd_fantasy_rpg.domain.common.base_exceptions import DomainError

# === Battle ===
class BattleNotFoundError(DomainError):
    """Активный бой не найден."""

    def __init__(self, player_id: str):
        self.player_id = player_id
        super().__init__(f"Active battle not found for player {player_id}")


class BattleAlreadyFinishedError(DomainError):
    """Бой уже завершен."""
    pass


class CombatantNotAliveError(DomainError):
    """Оба бойца должны быть живы для начала боя."""
    pass


class CombatantNotInBattleError(DomainError):
    """Боец не участвует в этом бою."""
    pass


class NotYourTurnError(DomainError):
    """Сейчас не ваш ход."""
    pass

