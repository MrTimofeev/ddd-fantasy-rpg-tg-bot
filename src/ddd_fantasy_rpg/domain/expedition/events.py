from dataclasses import dataclass

from ddd_fantasy_rpg.domain.expedition.expedition_event import ExpeditionEvent
from ddd_fantasy_rpg.domain.common.domain_event import DomainEvent

@dataclass
class ExpeditionStarted(DomainEvent):
    expedition_id: str
    player_id: str
    
@dataclass
class ExpeditionCompleted(DomainEvent):
    expedition_id: str
    player_id: str
    outcome: ExpeditionEvent