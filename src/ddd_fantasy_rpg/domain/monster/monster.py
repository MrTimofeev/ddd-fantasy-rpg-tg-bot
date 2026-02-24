from dataclasses import dataclass
from typing import List

from ..shared.item import Item


@dataclass(frozen=True)
class Monster:
    name: str
    level: int
    base_damage: int
    max_hp: int
    drop_items: List[Item]
    flee_difficulty: int # влияет на шас побега (1-100)
    
    def __post_init__(self):
        if self.level < 1:
            raise ValueError("Monster level must be >=1")
        if self.flee_difficulty < 1 or self.flee_difficulty > 100:
            raise ValueError("Flee difficulty must be between 1 and 100")