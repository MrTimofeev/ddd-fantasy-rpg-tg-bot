from enum import Enum
from dataclasses import dataclass, field
from typing import Dict


class ItemType(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    HELMET = "helmet"
    CONSUMABLE = "consumble"
    RESOURCE = "resource"
    
@dataclass(frozen=True)
class ItemStats:
    """Бонусы от предмета."""
    strength: int = 0
    agility: int = 0
    intelligence: int = 0
    max_hp: int = 0
    damage: int = 0
    
    
@dataclass(frozen=True)
class Item:
    id: str
    name: str
    item_type: ItemType
    level_required: int
    rarity: int # 1-5
    stats: ItemStats = field(default_factory=ItemStats)
    
    def __post_init__(self):
        if not (1 <= self.rarity <= 5):
            raise ValueError("Rarity must be between 1 and 5")
        if self.level_required < 1:
            raise ValueError("Level required must be >= 1")
        
    