from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class ItemDTO:
    id: str
    name: str
    item_type: str
    level_required: int
    rarity: int
    stats: Dict[str, str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ItemDTO":
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "item_type": self.item_type,
            "level_required": self.level_required,
            "rarity": self.rarity,
            "stats": self.stats,
        }


@dataclass
class CombatantDTO:
    id: str
    name: str
    combatant_type: str
    stats: Dict[str, int]
    current_hp: int
    skills: List[Dict[str, Any]]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CombatantDTO":
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items()}
