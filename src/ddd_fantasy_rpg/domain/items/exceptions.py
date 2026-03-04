from ddd_fantasy_rpg.domain.common.base_exceptions import DomainError

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
