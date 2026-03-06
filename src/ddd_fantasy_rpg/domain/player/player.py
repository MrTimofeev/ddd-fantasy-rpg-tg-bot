from dataclasses import dataclass, field
from collections import deque
from typing import Optional, List
from datetime import datetime, timezone, timedelta

from ddd_fantasy_rpg.domain.items.item_instance import ItemInstance
from ddd_fantasy_rpg.domain.items.item_type import ItemType
from ddd_fantasy_rpg.domain.player.character_stats import CharacterStats
from ddd_fantasy_rpg.domain.player.inventory import Inventory
from ddd_fantasy_rpg.domain.player.equipment import Equipment

from ddd_fantasy_rpg.domain.common.base_exceptions import DomainError

from ddd_fantasy_rpg.domain.player.race import Race
from ddd_fantasy_rpg.domain.player.player_profession import PlayerClass
from ddd_fantasy_rpg.domain.player.events import PlayerGainedExperience, PlayerLevelUp, PlayerDied, PlayerDefetedByPlayer, PlayerDefetedByMonster, PlayerRevived, SkillChanged, PlayerCreated
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

    # Экономика
    _gold: int = 0
    # Минимальный порог золота, не теряемый присмерти игрока
    _min_gold_thereshold: int = 0

    # Состояние
    _current_hp: int = field(init=False)
    _inventory: Inventory = field(default_factory=Inventory)
    _equipment: Equipment = field(default_factory=Equipment)

    # Навыки: 3 Слота
    _skill_slots: List[Optional[str]] = field(
        default_factory=lambda: [None, None, None])

    # Смерть и возраждение
    _is_dead: bool = field(default=False, init=False)
    _death_timestamp: Optional[datetime] = field(default=None, init=False)

    # События
    _pending_events: List[DomainEvent] = field(
        default_factory=list, repr=False)

    def __post_init__(self):
        total_stats = self.get_total_stats()
        self._current_hp = total_stats.max_hp
        
        self._pending_events.append(PlayerCreated(
            player_id=self.id,
            player_race=self.race,
            player_class=self.profession,
        ))


    @property
    def current_hp(self) -> int:
        return self._current_hp

    @property
    def is_alive(self) -> bool:
        return not self._is_dead

    @property
    def gold(self) -> int:
        return self._gold
    
    @property
    def can_access_guild_storage(self) -> bool:
        """Доступ к сундуку только если он жив и не в бою/экспедиции"""
        return self.is_alive

    def add_gold(self, amount: int):
        if amount < 0:
            raise DomainError("Cумма не может быть отрицательной.")
        self._gold += amount

    def send_gold(self, amount: int):
        if self._gold - amount < 0:
            raise DomainError("Недостаточно золота")
        self._gold -= amount

    def set_min_gold_threshold(self, amount: int):
        """Устанаваливается через улучшение гильдии"""
        if amount < 0:
            raise DomainError("Пороговое значение не может быть отрицательным")

        self._min_gold_thereshold = amount

    def get_inventory_items(self) -> list[ItemInstance]:
        return self._inventory.get_items()

    def get_equipped_items(self) -> dict:
        return self._equipment.get_equipped_items()

    def take_damage(self, damage: int) -> None:
        if self._is_dead:
            return

        effective_damage = max(1, damage - self.get_total_stats().armor)
        self._current_hp = max(0, self._current_hp - effective_damage)

    def take_heal(self, heal_amount: int) -> int:
        if self._is_dead:
            return 0
        max_hp = self.get_total_stats().max_hp
        missing_hp = max_hp - self._current_hp
        actual_heal = min(heal_amount, missing_hp)
        self._current_hp += actual_heal
        return actual_heal

    def die(self, killer_id: Optional[str] = None) -> List[ItemInstance]:
        """
        Killer_id: ID убийцы (игрок). Если None - смерть от монстра/среды.
        Возвращает список предметов (ItemInstance), которые должны быть переданы или удалены.
        """

        if self._is_dead:
            return []

        self._is_dead = True
        self._current_hp = 0
        self._death_timestamp = datetime.now(timezone.utc)

        if killer_id is not None:
            # PVP
            # 1. Сбрасываем золото до порога
            lost_gold = max(0, self._gold - self._min_gold_thereshold)
            self._gold = self._min_gold_thereshold

            # 2. Весь инвентарь переходить победителю
            droped_items = self._inventory.get_items()
            self._inventory.items.clear()  # Очищаем инвентарь умершего

            # 3. Снимаем шмотки
            for slot_name in ['weapon', 'armor', 'helmet', 'ring', 'boots']:
                item = self._equipment.unequip(slot_name)
                if item:
                    droped_items.append(item)
# 
            self._pending_events.append(PlayerDefetedByPlayer(
                victim_id=self.id,
                victor_id=killer_id,
                lost_gold=lost_gold,
                transferred_item_ids=[i.id for i in droped_items]
            ))
        else:
            # PVE

            # 1. Отчищаем инвентарь
            droped_items = self._inventory.get_items()
            self._inventory.items.clear()

            # Снимаем экипировку и добавляем в потерянный лут
            for slot_name in ['weapon', 'armor', 'helmet', 'ring', 'boots']:
                item = self._equipment.unequip(slot_name)
                if item:
                    droped_items.append(item)

            self._pending_events.append(PlayerDefetedByMonster(
                player_id=self.id,
                lost_item_ids=[i.id for i in droped_items]
            ))

        self._pending_events.append(PlayerDied(player_id=self.id))
        return droped_items

    def try_respawn(self, current_time: datetime) -> bool:
        """Попытка возраждения. Возвращает True если успешно."""
        if not self._is_dead:
            return True

        if self._death_timestamp is None:
            raise DomainError(
                "Игрок отмечен как погибший но время смерти не указано")

        # Расчет времени сметри: чем больше уровень тем дольше время воскришения
        # Базовое время 5 миинут + 2 минут за каждый уровень
        cooldown_minutes = 5 + (self.level * 2)
        respawn_time = self._death_timestamp + \
            timedelta(minutes=cooldown_minutes)

        if current_time >= respawn_time:
            self._is_dead = False
            self._current_hp = self.get_total_stats().max_hp
            self._death_timestamp = None
            self._pending_events.append(PlayerRevived(player_id=self.id))
            return True
        return False

    def get_active_skills(self) -> List[Optional[str]]:
        """Возвращает копию списка активных скиллов (ID шаблонов)"""
        return self._skill_slots.copy()

    def change_skill(self, slot_index: int, new_skill_template_id: str, scroll_item: ItemInstance):
        """
        Меняет навык в слоте. Требует наличия предмета "Свиток навыка"
        """

        if not (0 <= slot_index <= 2):
            raise DomainError(
                "Неверный индекс слота навыка. Должен быть 0, 1 или 2.")

        # Проверяет тип предмета
        if scroll_item.item_type != ItemType.SCROLL and "Свиток навыка" not in scroll_item.name:
            raise DomainError(
                "Требуется предмет типа SCROLL с названием 'Свиток навыка'")

        # Проверка наличия свитка в инвентаре
        if not self._inventory.find_item_by_id(scroll_item.id):
            raise DomainError("Свиток не найден в инвентаре игрока")

        old_skill = self._skill_slots[slot_index]

        # Применяем изменения
        self._skill_slots[slot_index] = new_skill_template_id

        # Удаляем из инвентаря
        self._inventory.remove_item(scroll_item.id)

        self._pending_events.append(SkillChanged(
            player_id=self.id,
            slot_index=slot_index,
            new_skill_id=new_skill_template_id,
            old_skill_id=old_skill
        ))

    def add_exp(self, amount: int) -> bool:
        if self._is_dead:
            return False

        self.exp += amount
        old_level = self.level
        new_level = 1 + (self.exp // 100)
        
        leveled_up = False
        if new_level > old_level:
            self._level = new_level
            # TODO: добавить логику начинсление статок за уровень
            self._pending_events.append(PlayerLevelUp(
                player_id=self.id,
                new_level=self.level,
                gained_stats={"hp": 10} # Заглушка
            ))
            leveled_up = True


        self._pending_events.append(PlayerGainedExperience(
            player_id=self.id,
            exp_gained=amount
        ))
        return leveled_up


    def add_item_to_inventory(self, item: "ItemInstance") -> None:
        item.owner_id = self.id
        self._inventory.add_item(item)

    def equip_item(self, item_id: str) -> None:
        item = self._inventory.find_item_by_id(item_id)
        if not item:
            raise DomainError(
                f"Невозможно экипировать предмет с ID '{item_id}': он не найден в инвентаре.")
        if item.is_equipped:
            raise DomainError("Предмет уже экипирован")
        
        #Снимаем предмет из инвентаря
        item = self._inventory.remove_item(item_id)
        #экипируем
        self._equipment.equip(item)

    def uneqip_item(self, slot_name: str) -> None:
        item = self._equipment.unequip(slot_name)
        if item:
            item.uneqip()
            self._inventory.add_item(item)
            
    def use_item(self, item_id: str) -> dict:
        """
        Использовать предмет из инвентаря (вне боя).
        Возвращает результат использования (например, сколько восстановлено HP).
        """
        if self._is_dead:
            raise DomainError("Нельзя использовать предметы, когда вы мертвы")
        
        item = self._inventory.find_item_by_id(item_id)
        if not item:
            raise DomainError("Предмет не найден в инвентаре")
        
        if not item.is_consumable():
            raise DomainError("Этот предмет нельзя испоьзовать напрямую (возможно, его нужно экипировать)")
        
        # получаем инструкцию от предмета
        context = {
            "current_hp": self._current_hp,
            "max_hp": self.get_total_stats().max_hp,
            "skills": self._skill_slots
        }
        
        useage_instruction = item.use_consumable(context)
        
        result = {
            "used_item_id": item_id, 
            "item_name": item.name,
            "effects": []
        }
        
        if useage_instruction["action"] == "heal":
            healed_amount = self.take_heal(useage_instruction['value'])
            result["effects"].append({
                "type": "heal",
                "amount": healed_amount
            })
            
            self._inventory.remove_item(item_id)
        elif useage_instruction["action"] == "change_skill":
            result["effects"].append({
                "type": "ready_for_skill_change",
                "scroll_id": item_id
            })
            
        else:
            raise DomainError(f"Неизвестный эффект предмета: {useage_instruction["action"]}")
        
        return result
        

    def get_total_stats(self) -> CharacterStats:
        equipment_stats = self._equipment.get_total_equipment_stats()
        return self.base_stats + equipment_stats

    def get_base_stats(self) -> CharacterStats:
        return self.base_stats

    def get_exp_needed_for_next_level(self) -> int:
        return (self.level * 100) - (self.exp % 100)

    def pop_pending_events(self) -> list[DomainEvent]:
        events = list(self._pending_events)
        self._pending_events.clear()
        return events
    
    def __repr__(self) -> str:
        return f"<Player id={self.id} name={self.name} level={self.level} hp={self._current_hp}/{self.get_total_stats().max_hp}>"
