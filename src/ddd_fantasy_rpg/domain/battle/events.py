from dataclasses import dataclass

from ddd_fantasy_rpg.domain.battle.battle_result import BattleResult
from ddd_fantasy_rpg.domain.common.domain_event import DomainEvent

@dataclass
class BattleStarted(DomainEvent):
    battle_id: str
    attacker_id: str
    defender_id: str
    
@dataclass
class BattleFinished(DomainEvent):
    battle_id: str
    result: BattleResult
    winner_id: str
    loser_id: str
