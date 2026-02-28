from dataclasses import dataclass, field

from .item_type import ItemType
from .item_rarity import Rarity
   
   
    
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
    name: str
    item_type: ItemType
    level_required: int
    rarity: Rarity
    stats: ItemStats = field(default_factory=ItemStats)
    
    def __post_init__(self):
        if self.level_required < 1:
            raise ValueError("Level required must be >= 1")
        
    