from typing import Dict

from ddd_fantasy_rpg.domain.items.item_type import ItemType
from ddd_fantasy_rpg.domain.items.item_instance import ItemInstance
from ddd_fantasy_rpg.domain.items.exceptions import CannotEquipItemError

class EquipmentService:
    """Доменный серсив для управления экиписровкой"""
    
    # Конфигурация маппинга типов предметов на слоты
    _SLOT_MAPPING: Dict[ItemType, str] = {
        ItemType.WEAPON: "weapon",
        ItemType.ARMOR: "armor",
        ItemType.HELMET: "helmet",
        ItemType.RING: "ring",
        ItemType.BOOTS: "boots",
        ItemType.POTION: "consumable",
        ItemType.POTION: "consumable"
    }
    
    @classmethod
    def get_slot_for_item_type(cls, item_type: ItemType) -> str:
        """Возвращает слот для данного предмета."""
        if item_type not in cls._SLOT_MAPPING:
            raise CannotEquipItemError(f"Cannot quip item type: {item_type.value}")
        return cls._SLOT_MAPPING[item_type]
    
    @classmethod
    def can_equip_item(cls, player_level: int, item: ItemInstance) -> bool:
        """Проверят, может ли игрок экипироваь предмет."""
        return item <= player_level