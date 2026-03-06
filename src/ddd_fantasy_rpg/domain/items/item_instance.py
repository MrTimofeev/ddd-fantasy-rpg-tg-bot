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
        
    def is_consumable(self) -> bool:
        return self.item_type in [ItemType.POTION, ItemType.SCROLL, ItemType.CONSUMABLE]
    
    def is_equippable(self) -> bool:
        return self.item_type in [ItemType.WEAPON, ItemType.ARMOR, ItemType.HELMET, ItemType.RING, ItemType.BOOTS]
    
    def is_resource(self) -> bool:
        return self.item_type == ItemType.RESOURCE
    
    def use_consumable(self, context: dict) -> dict:
        """
        Базовая проверка пред использованием расходника.
        Возвращает данные о том, какой эффект применить.
        Сам эффект применяется в Player или BattleService.
        """
        
        if not self.is_consumable():
            raise DomainError(f"Предмет {self.name} не расходник")
        
        # TODO: сделать нормальный VO а не возвращать dict
        if self.item_type == ItemType.POTION:
            heal_amount = self.stats.max_hp if self.stats.max_hp > 0 else 50
            return {
                "action": "heal",
                "value": heal_amount,
                "source_item_id": self.id
            }
        elif self.item_type == ItemType.SCROLL:
            if "Свиток Навыка" in self.name:
                return {
                    "action": "change_skill",
                    "source_item_id": self.id
                }
            else:
                # Другие свитки
                return {
                    "action": "неизвеснтное дейтсие",
                    "source_item_id": self.id
                }
        
        raise DomainError(f"Логика использования элемента {self.name} не реализована.")
    
        
    def __repr__(self) -> str:
        return f"ItemInstance(id={self.id}, name={self.name}, type={self.item_type.value})"