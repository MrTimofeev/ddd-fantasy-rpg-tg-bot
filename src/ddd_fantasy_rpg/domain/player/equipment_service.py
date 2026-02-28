from typing import Dict

from ddd_fantasy_rpg.domain.items.item import Item, ItemType
from ddd_fantasy_rpg.domain.items.exeptions import CannotEquipItemError

class EquiupmentSevice:
    """Доменный серсив для управления экиписровкой"""
    
    # Конфигурация маппинга типов предметов на слоты
    _SLOT_MAPPING: Dict[ItemType, str] = {
        ItemType.WEAPON: "weapon",
        ItemType.ARMOR: "armor",
        ItemType.HELMET: "helmet",
        ItemType.RING: "ring",
        ItemType.BOOTS: "boots",
    }
    
    @classmethod
    def get_slot_for_item_type(cls, item_type: ItemType) -> str:
        """Возвращает слот для данного предмета."""
        if item_type not in cls._SLOT_MAPPING:
            raise CannotEquipItemError(f"Cannot quip item type")
        return cls._SLOT_MAPPING[item_type]
    
    @classmethod
    def can_equip_item(cls, player_level: int, item: Item) -> bool:
        """Проверят, может ли игрок экипироваь предмет."""
        return item.level_required <= player_level