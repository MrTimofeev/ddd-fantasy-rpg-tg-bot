from dataclasses import dataclass, field
from collections import deque
from typing import Optional
from datetime import datetime, timezone, timedelta

from ddd_fantasy_rpg.domain.items.item_instance import ItemInstance
from ddd_fantasy_rpg.domain.player.character_stats import CharacterStats
from ddd_fantasy_rpg.domain.player.inventory import Inventory
from ddd_fantasy_rpg.domain.player.equipment import Equipment

from ddd_fantasy_rpg.domain.common.base_exceptions import DomainError

from ddd_fantasy_rpg.domain.player.race import Race
from ddd_fantasy_rpg.domain.player.player_profession import PlayerClass
from ddd_fantasy_rpg.domain.player.events import PlayerGainedExperience, PlayerLevelUp
from ddd_fantasy_rpg.domain.common.domain_event import DomainEvent


@dataclass
class Player:
    id: str
    telegram_id: int
    name: str
    race: Race
    profession: PlayerClass
    level: int
    exp: int

    base_stats: CharacterStats

    _current_hp: int = field(init=False)
    _inventory: Inventory = field(default_factory=Inventory)
    _equipment: Equipment = field(default_factory=Equipment)
    _is_dead: bool = field(default=False, init=False)
    _death_timestamp: Optional[datetime] = field(default=None, init=False)
    _respawn_delay_seconds: int = field(default=600, init=False)

    def __post_init__(self):
        self._current_hp = self.base_stats.max_hp
        self._pending_events: deque[DomainEvent] = deque()

    @property
    def current_hp(self) -> int:
        return self._current_hp

    @property
    def is_alive(self) -> bool:
        return not self._is_dead

    def get_inventory_items(self) -> list:
        return self._inventory.get_items()

    def get_equipped_items(self) -> dict:
        return self._equipment.get_equipped_items()

    def take_damage(self, damage: int) -> None:
        if self._is_dead:
            raise DomainError("Нельзя нанести урон мертвому")

        effective_damage = max(
            1, damage - self._equipment.get_total_equipment_stats().armor)
        self._current_hp = max(0, self._current_hp - effective_damage)

        if self._current_hp <= 0:
            self.die()

    def take_heal(self, heal_amount: int) -> int:

        if self._is_dead:
            raise DomainError("Нельзя лечить мертвого")

        max_heal = self.get_total_stats().max_hp - self._current_hp
        actual_heal = min(heal_amount, max_heal)
        self._current_hp += actual_heal
        return actual_heal

    def die(self) -> None:
        if self._is_dead:
            return

        self._is_dead = True
        self._death_timestamp = datetime.now(timezone.utc)

    def try_respawn(self, time_provider) -> bool:
        if not self._is_dead:
            return True

        if self._death_timestamp is None:
            raise DomainError(
                "Игрок отмечен как погибший но время смерти не указано")

        if time_provider.now() >= self._death_timestamp + timedelta(seconds=self._respawn_delay_seconds):
            self._current_hp = max(1, self.get_total_stats().max_hp // 4)
            self._is_dead = False
            self._death_timestamp = None
            return True
        return False

    def add_exp(self, amount: int) -> bool:

        if amount <= 0:
            return False

        self.exp += amount
        old_level = self.level

        new_level = 1 + (self.exp // 100)
        if new_level > old_level:
            self._level = new_level

            self.base_stats = CharacterStats(
                strength=self.base_stats.strength +
                (new_level - old_level) * 1,
                agility=self.base_stats.agility + (new_level - old_level) * 1,
                intelligence=self.base_stats.intelligence +
                (new_level - old_level) * 1,
                max_hp=self.base_stats.max_hp + (new_level - old_level) * 5,
                damage=self.base_stats.damage + (new_level - old_level) * 1,
                armor=self.base_stats.armor,
            )

            self._current_hp = min(self._current_hp, self.base_stats.max_hp)

            event = PlayerLevelUp(player_id=self.id, new_level=new_level, gained_stats={
                                  'strength': 1, 'max_hp': 5})
            self._pending_events.append(event)

            return True

        else:
            event = PlayerGainedExperience(
                player_id=self.id, exp_gained=amount)
            self._pending_events.append(event)

        return False

    def pop_pending_events(self) -> list[DomainEvent]:
        events = list(self._pending_events)
        self._pending_events.clear()
        return events

    def add_item_to_inventory(self, item: "ItemInstance") -> None:
        self._inventory.add_item(item)

        item.owner_id = self.id

    def equip_item(self, item_id: str) -> None:

        item = self._inventory.find_item_by_id(item_id)
        if not item:
            raise DomainError(
                f"Невозможно экипировать предмет с ID '{item_id}': он не найден в инвентаре.")

        item = self._inventory.remove_item(item_id)

        self._equipment.equip(item)

    def uneqip_item(self, slot_name: str) -> None:
        item = self._equipment.unequip(slot_name)

        if item:
            self._inventory.add_item(item)

    def get_total_stats(self) -> CharacterStats:
        equipment_stats = self._equipment.get_total_equipment_stats()
        return self.base_stats + equipment_stats

    def get_base_stats(self) -> CharacterStats:
        return self.base_stats

    def get_exp_needed_for_next_level(self) -> int:
        return 100 * (self.level + 1) - self.exp

    def __repr__(self) -> str:
        return f"<Player id={self.id} name={self.name} level={self.level} hp={self._current_hp}/{self.get_total_stats().max_hp}>"
