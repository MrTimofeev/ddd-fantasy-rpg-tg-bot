from dataclasses import dataclass
from typing import Dict, Any

@dataclass(frozen=True)
class CharacterStats:
    """
    Статы персонажа, включая базовые статы, бонусы от экипировки.
    """
    strength: int = 0
    agility: int = 0
    intelligence: int = 0
    max_hp: int = 0
    damage: int = 0
    armor: int = 0 
    
    def __add__(self, other: 'CharacterStats') -> 'CharacterStats':
        """
        Комбинирует характеристики
        """
        if not isinstance(other, CharacterStats):
            return NotImplemented
        return CharacterStats(
            strength=self.strength + other.strength,
            agility=self.agility + other.agility,
            intelligence=self.intelligence + other.intelligence,
            max_hp=self.max_hp + other.max_hp,
            damage=self.damage + other.damage,
            armor=self.armor + other.armor,
        )
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CharacterStats':
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})
    