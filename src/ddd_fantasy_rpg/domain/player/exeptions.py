from ddd_fantasy_rpg.domain.common.base_exceptions import DomainError

# === Player ===
class PlayerNotFoundError(DomainError):
    """Игрок не найден."""

    def __init__(self, player_id: str = ""):
        self.player_id = player_id
        super().__init__(f"Player {player_id} not found")


class PlayerAlreadyInBattleError(DomainError):
    """Игрок уже находится в бою."""

    def __init__(self, player_id: str):
        self.player_id = player_id
        super().__init__(f"Player {player_id} is already in battle")


class PlayerAlreadyOnExpeditionError(DomainError):
    """Игрок уже находится в экспедиции"""

    def __init__(self, player_id: str):
        self.player_id = player_id
        super().__init__(f"Player {player_id} is already on an expedition")

class PlayerAlreadyExistingError(DomainError):
    """Игрок уже существует."""
    def __ini__(self, player_id: str):
        self.player_id = player_id
        super().__init__(f"Player with ID {player_id} already exists")
        
class SelfDuelError(DomainError):
    pass

