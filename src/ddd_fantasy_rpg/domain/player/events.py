from dataclasses import dataclass
from typing import Dict, Any

from ddd_fantasy_rpg.domain.common.domain_event import DomainEvent
from ddd_fantasy_rpg.domain.items.item_instance import ItemInstance


@dataclass
class PlayerLevelUp(DomainEvent):
    player_id: str
    new_level: int
    gained_stats: Dict[str, int]


@dataclass
class PlayerDied(DomainEvent):
    player_id: str


@dataclass
class PlayerReceivedLoot(DomainEvent):
    player_id: str
    items: list[ItemInstance]


@dataclass
class PlayerGainedExperience(DomainEvent):
    player_id: str
    exp_gained: int
