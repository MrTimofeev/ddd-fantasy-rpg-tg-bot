from dataclasses import dataclass
from typing import Dict, Any

from ddd_fantasy_rpg.domain.skills.skill_type import SkillType


@dataclass(frozen=True)
class SkillTemplate:
    """Шаблон скилла - определение типа способности."""
    id: str
    name: str
    skill_type: SkillType
    base_power: int
    cooldown_turns: int
    level_required: int
    description: str = ""
    
    # Дополнительные параметры для разнытих типов килоов
    additional_params: Dict[str, Any] = None
    
    @classmethod
    def from_dict(cls, data: Dict) -> "SkillTemplate":
        
         return cls(
            id=data['id'],
            name=data['name'],
            skill_type=SkillType(data['type']),
            base_power=data['base_power'],
            cooldown_turns=data['cooldown_turns'],
            level_required=data.get('level_required', 1),
            description=data.get('description', ''),
            additional_params=data.get('additional_params', {})
        )