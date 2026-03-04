from dataclasses import dataclass, field
from typing import Optional, Dict

from ddd_fantasy_rpg.domain.items.item_type import ItemType
from ddd_fantasy_rpg.domain.player.character_stats import CharacterStats
from ddd_fantasy_rpg.domain.common.base_exceptions import DomainError


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
    
    _is_equipped: bool = field(default=False, repr=False)
    _slot: Optional[str] = field(default=None, repr=False)
    modifiers: Dict[str, int] = field(default_factory=dict)
    
    
    @property 
    def is_equipped(self) -> bool:
        return self._is_equipped
    
    @property
    def slot(self) -> Optional[str]:
        return self._slot
    
    def equip(self, slot_name: str) -> None:
        if self._is_equipped:
            raise DomainError("Предмет уже экипирован в слот")
        
        self._is_equipped = True 
        self._slot = slot_name
        
    def uneqip(self) -> None:
        if not self._is_equipped:
            raise DomainError("Предмет не экипирован")
        self._is_equipped = False
        self._slot = None
        