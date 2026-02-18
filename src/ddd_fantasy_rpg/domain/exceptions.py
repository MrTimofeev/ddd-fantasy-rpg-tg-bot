class DomainError(Exception):
    """Базовый класс для всех доменных исключений."""
    pass


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


# === Skills ===
class SkillNotAvailableError(DomainError):
    """Скилл недоступен для этого бойца."""

    def __init__(self, skill_name: str):
        self.skill_name = skill_name
        super().__init__(
            f"Skill '{skill_name}' is not available to this combatant")


class SkillOnCooldownError(DomainError):
    """Скилл находится на перезарядке."""

    def __init__(self, skill_name: str):
        self.skill_name = skill_name
        super().__init__(f"Skill '{skill_name}' is on cooldown")


# === Items ===
class InsufficientLevelError(DomainError):
    """Недостаточный уровень для экипировки предмета."""

    def __init__(self, item_name: str, required_level: int, current_level: int):
        self.item_name = item_name
        self.required_level = required_level
        self.current_level = current_level
        super().__init__(
            f"Item '{item_name}' requires level {required_level}, but player is level {current_level}"
        )


class CannotEquipItemError(DomainError):
    """Невозможно экипировать предмет такого типа."""

    def __init__(self, item_type: str):
        self.item_type = item_type
        super().__init__(f"Cannot equip item of type {item_type}")
