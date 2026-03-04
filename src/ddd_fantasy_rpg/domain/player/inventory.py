from dataclasses import dataclass, field
from typing import List, Optional

from ddd_fantasy_rpg.domain.items.item_instance import ItemInstance
from ddd_fantasy_rpg.domain.common.base_exceptions import DomainError



@dataclass
class Inventory:
    items: list[ItemInstance] = field(default_factory=list)
    max_size: int = 20
    
    def add_item(self, item: ItemInstance) -> None:
        if len(self.items) >= self.max_size:
            raise DomainError("Инвентарь заполнен")
        self.items.append(item)
        
    def remove_item(self, item_id: str) -> ItemInstance:
        for i, item in enumerate(self.items):
            if item.id == item_id:
                return self.items.pop(i)
        raise DomainError("Предмет в инвентаре не найден")
    
    def find_item_by_id(self, item_id: str) -> Optional[ItemInstance]:
        return next((item for item in self.items if item.id == item_id), None)
    
    
    def get_items(self) -> List[ItemInstance]:
        return self.items[:]        