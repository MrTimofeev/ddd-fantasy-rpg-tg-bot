from dataclasses import dataclass, field
from typing import Optional, Dict

from ddd_fantasy_rpg.domain.items.item_type import ItemType
from ddd_fantasy_rpg.domain.common.stats import CharacterStats


@dataclass
class ItemInstance:
    """Конкретный экземпляр предмета, принадлащий игроку."""
    id: str # Уникальный ID экзепляра 
    name: str
    template_id: str # Ссылка на шаблон
    level_required: int
    item_type: ItemType
    stats: CharacterStats
    owner_id: Optional[str] = None
    is_equipped: bool = False
    slot: Optional[str] = None
    
    # Дополнительные модификаторы (для уникальных предметов)
    modifiers: Dict[str, int] = field(default_factory=dict)
    
    
    def equip(self, slot_name: str) -> None:
        if self.is_equipped:
            return
        self.is_equipped = True
        self.slot = slot_name
    
    def unequip(self) -> None:
        self.is_equipped = False
        self.slot = None