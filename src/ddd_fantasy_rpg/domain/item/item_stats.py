from dataclasses import dataclass


@dataclass(frozen=True)
class ItemStats:
    strength: int = 0
    agility: int = 0
    intelligence: int = 0
    max_hp: int = 0
    damage: int = 0
