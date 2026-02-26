from ddd_fantasy_rpg.domain.common.base_exceptions import DomainError

# === Expedition ===
class ExpeditionNotFoundError(DomainError):
    """Экспедиция не найдена."""

    def __init__(self, player_id: str):
        self.player_id = player_id
        super().__init__(f"Expedition for player {player_id} not found")


class ExpeditionAlreadyFinishedError(DomainError):
    """Экспедиция уже завершена."""
    pass


class ExpeditionNotFinishedError(DomainError):
    """Экспедиция ещё не завершена."""
    pass


class ExpeditionNotActiveError(DomainError):
    """Нельзя прервать неактивную экспедицию."""
    pass


class NoActiveExpeditionFoundError(DomainError):
    """Активных экспедиций не найдено"""
    pass

