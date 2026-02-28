from typing import List

from ddd_fantasy_rpg.domain.items.item import Item
from ddd_fantasy_rpg.domain.player.race import Race
from ddd_fantasy_rpg.domain.player.player_profession import PlayerClass

from ddd_fantasy_rpg.domain.player.equipment_service import EquiupmentSevice
from ddd_fantasy_rpg.domain.player.stats_calculation_service import StatsCalculationService




class Player:
    def __init__(
        self,
        player_id: str,
        telegram_id: int,
        name: str,
        race: Race,
        player_profession: PlayerClass,
    ):
        if not name.strip():
            raise ValueError("Player name cannot be empty")
        if race not in Race:
            raise ValueError("Invalid race")
        if player_profession not in PlayerClass:
            raise ValueError("Invalid class")

        self._id = player_id
        self._telegram_id = telegram_id
        self._name = name.strip()
        self._race = race
        self._profession = player_profession
        self._level = 1
        self._exp = 0
        self._inventory: List[Item] = []
        self._equipped: dict[str, Item] = {}  # например: {"weapon": item}

        self._base_stats = StatsCalculationService.calculate_base_stats(race, player_profession)

    @property
    def id(self) -> str:
        return self._id

    @property
    def telegram_id(self) -> int:
        return self._telegram_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def race(self) -> Race:
        return self._race

    @property
    def profession(self) -> PlayerClass:
        return self._profession

    @property
    def level(self) -> int:
        return self._level
    
    @property
    def exp(self) -> int:
        return self._exp

    @property
    def inventory(self) -> List[Item]:
        return self._inventory.copy()

    def add_item(self, item: Item) -> None:
        """ Добавить предмет в инвентарь"""
        self._inventory.append(item)

    def equip_item(self, item: Item) -> None:
        """ Экипировать предмет в слот (например, 'weapon', 'helmet')."""
        
        if not EquiupmentSevice.can_equip_item(self.level, item):
            raise ValueError(
                f"Item '{item.name}' requires level {item.level_required}, "
                f"But player is level {self._level}"
            )
        
        slot = EquiupmentSevice.get_slot_for_item_type(item.item_type)
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
