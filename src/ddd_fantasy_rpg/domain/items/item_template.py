from dataclasses import dataclass
from typing import Dict

from ddd_fantasy_rpg.domain.items.item_type import ItemType
from ddd_fantasy_rpg.domain.items.item_stats import ItemStats
from ddd_fantasy_rpg.domain.items.item_rarity import Rarity

@dataclass(frozen=True)
class ItemTemplate:
    """Шаблон предмета - определение типа предмета."""
    id: str
    name: str
    item_type: ItemType
    rarity: Rarity
    level_required: int
    stats: ItemStats
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ItemTemplate":
        """Создаёт шаблон из словаря (для загрузки из YAML)."""
        stats_data = data.get('stats', {})
        stats = ItemStats(
            strength=stats_data.get('strength', 0),
            agility=stats_data.get('agility', 0),
            intelligence=stats_data.get('intelligence', 0),
            max_hp=stats_data.get('max_hp', 0),
            damage=stats_data.get('damage', 0),
        )
        
        return cls(
            id=data['id'],
            name=data['name'],
            item_type=ItemType(data['type']),
            rarity=Rarity(data['rarity']),
            level_required=data['level_required'],
            stats=stats
        )
    