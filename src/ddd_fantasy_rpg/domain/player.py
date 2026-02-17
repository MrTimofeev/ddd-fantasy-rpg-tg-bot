from enum import Enum
from typing import List

from .item import Item, ItemType


class Race(Enum):
    HUMAN = "human"
    ELF = "elf"
    ORC = "orc"
    DWARF = "dwarf"


class PlayerClass(Enum):
    WARRIOR = "warrior"
    MAGE = "mage"
    ROGUE = "rogue"
    PALADIN = "paladin"


class Player:
    def __init__(
        self,
        player_id: str,
        telegram_id: int,
        name: str,
        race: Race,
        player_class: PlayerClass,
    ):
        if not name.strip():
            raise ValueError("Player name cannot be empty")
        if race not in Race:
            raise ValueError("Invalid race")
        if player_class not in PlayerClass:
            raise ValueError("Invalid class")

        self._id = player_id
        self._telegram_id = telegram_id
        self._name = name.strip()
        self._race = race
        self._class = player_class
        self._level = 1
        self._exp = 0
        self._inventory: List[Item] = []
        self._equipped: dict[str, Item] = {}  # например: {"weapon": item}

        self._base_stats = self._calculate_base_stats()

    def _calculate_base_stats(self) -> dict:
        """ Базовые статы в зависимости от рассы и класса."""
        stats = {"strength": 10, "agility": 10, "intellegence": 10}

        # Пример бонусов
        if self._race == Race.ORC:
            stats["strength"] += 3

        if self._class == PlayerClass.WARRIOR:
            stats["strength"] += 2

        return stats

    @property
    def id(self) -> str:
        return self._id

    @property
    def level(self) -> int:
        return self._level

    @property
    def inventory(self) -> List[Item]:
        return self._inventory.copy()
    def add_item(self, item: Item) -> None:
        """ Добавить предмет в инвентарь"""
        self._inventory.append(item)

    def equip_item(self, item: Item, slot: str) -> None:
        """ Экипировать предмет в слот (например, 'weapon', 'helmet')."""
        if item.level_required > self._level:
            raise ValueError(
                f"Item '{item.name}' requires level {item.level_required}, but player is level {self._level}")

        slot_map = {
            ItemType.WEAPON: "weapon",
            ItemType.ARMOR: "armor",
            ItemType.HELMET: "helmet",
        }

        if item.item_type not in slot_map:
            raise ValueError(f"Cannot equip item of type {item.item_type}")

        slot = slot_map[item.item_type]
        self._equipped[slot] = item

    def get_total_stats(self) -> dict:
        """Возвращаем игровые статы (базовые + от экипировки)."""
        # TODO: Добавить бонус от преметов

        return self._base_stats.copy()

    def die(self) -> None:
        """Обрабатываем смерт игрока."""
        self._inventory.clear()
        # TODO: установить флаг смерти, время воскрешения и т.д.
        
    
    def __repr__(self) -> str:
        return f"<Player id={self._id} name={self._name} level={self._level}>"
