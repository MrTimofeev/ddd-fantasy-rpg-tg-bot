from dataclasses import dataclass, field
from typing import Optional, Dict

from ddd_fantasy_rpg.domain.items.item_template import ItemTemplate

@dataclass
class ItemInstance:
    """Конкретный экземпляр предмета, принадлащий игроку."""
    id: str # Уникальный ID экзепляра 
    template_id: str # Ссылка на шаблон
    owner_id: Optional[str] = None
    is_equipped: bool = False
    slot: Optional[str] = None
    
    # Дополнительные модификаторы (для уникальных предметов)
    modifiers: Dict[str, int] = field(default_factory=dict)
    
    @property
    def template(self) -> ItemTemplate:
        """Получаем шаблон предмета."""
        from ddd_fantasy_rpg.infrastructure.repositories.item_template_repository import ItemTemplateRepository
        return ItemTemplateRepository.get_tempalate(self.template_id)
        
    @property
    def total_stats(self) -> "ItemStats":
        from ddd_fantasy_rpg.domain.items.item_stats import ItemStats
        base = self.template.stats
        return ItemStats(
            strength=base.strength + self.modifiers.get("strength", 0),
            agility=base.agility + self.modifiers.get("agility", 0),
            intelligence=base.intelligence + self.modifiers.get("intelligence", 0),
            max_hp=base.max_hp + self.modifiers.get('max_hp', 0),
            damage=base.damage + self.modifiers.get('damage', 0),
        )
        