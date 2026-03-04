from dataclasses import dataclass, field
from typing import Dict, Optional, List

from ddd_fantasy_rpg.domain.items.item_instance import ItemInstance
from ddd_fantasy_rpg.domain.items.item_type import ItemType
from ddd_fantasy_rpg.domain.player.character_stats import CharacterStats
from ddd_fantasy_rpg.domain.common.base_exceptions import DomainError


@dataclass
class Equipment:
    _SLOT_MAPPING: Dict[str, List[ItemType]] = field(default_factory=lambda: {
        'weapon': [ItemType.WEAPON],
        'armor': [ItemType.ARMOR],
        'helmet': [ItemType.HELMET],
        'ring': [ItemType.RING],
        'boots': [ItemType.BOOTS],
    })
    
    weapon: Optional[ItemInstance] = None
    armor: Optional[ItemInstance] = None
    helmet: Optional[ItemInstance] = None
    ring: Optional[ItemInstance] = None
    boots: Optional[ItemInstance] = None
    
    def _get_slot_for_item_type(self, item_type: ItemType) -> Optional[str]:
        for slot_name, allowed_types in self._SLOT_MAPPING.items():
            if item_type in allowed_types:
                return slot_name
        return None
    
    def equip(self, item: ItemInstance) -> None:
        slot_name = self._get_slot_for_item_type(item.item_type)
        if not slot_name:
            raise DomainError("Предмет не может быть экипирован")
        
        current_item_in_slot = getattr(self, slot_name)
        
        setattr(self, slot_name, item)
        
        item.equip(slot_name)
        
        if current_item_in_slot:
            current_item_in_slot.unequip()
    
    def unequip(self, slot_name: str) -> Optional[ItemInstance]:
        if slot_name not in self._SLOT_MAPPING:
            raise DomainError("не действенный слот для снаряжения")
        
        current_item = getattr(self, slot_name)
        if current_item:
            current_item.unequip()
            setattr(self, slot_name, None)
        
        return current_item

    def get_total_equipment_stats(self) -> CharacterStats:
        total = CharacterStats()
        for slot_item in [self.weapon, self.armor, self.helmet, self.ring, self.boots]:
            if slot_item:
                total = total + slot_item.stats
        return total
    
    def get_equipped_items(self) -> Dict[str, Optional[ItemInstance]]:
        return {
            'weapon': self.weapon,
            'armor': self.armor,
            'helmet': self.helmet,
            'ring': self.ring,
            'boots': self.boots,
        }
    