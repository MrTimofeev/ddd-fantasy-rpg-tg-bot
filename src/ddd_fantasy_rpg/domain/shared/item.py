from enum import Enum
from dataclasses import dataclass, field


class ItemType(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    HELMET = "helmet"
    CONSUMABLE = "consumable"
    RESOURCE = "resource"
    
class Rarity(Enum):
    COMMON = 1
    UNCOMMON = 2
    RARE = 3
    EPIC = 4
    LEGENDARY = 5
    
    @staticmethod
    def from_level(level: int) -> "Rarity":
        """Преобразует уровень в редкость прeдмета."""
        if level >=9:
            return Rarity.LEGENDARY
        elif level >=7:
            return Rarity.EPIC
        elif level >=5:
            return Rarity.RARE
        elif level >=3:
            return Rarity.UNCOMMON
        else:
            return Rarity.COMMON
    
    
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
        
    