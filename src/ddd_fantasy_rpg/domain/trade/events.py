from dataclasses import dataclass
from typing import List

from ddd_fantasy_rpg.domain.common.domain_event import DomainEvent

@dataclass
class TradeSessionCreated(DomainEvent):
    trade_id: str
    initiator_id: str
    target_id: str
    
@dataclass
class TradeOfferUpdated(DomainEvent):
    traid_id: str
    player_id: str
    offered_item_ids: List[str]
    
@dataclass
class TradeAccepted(DomainEvent):
    trade_id: str
    player_id: str
    
@dataclass
class TradeRevoked(DomainEvent):
    trade_id: str
    player_id: str

@dataclass
class TradeCompleted(DomainEvent):
    trade_id: str
    initiator_id: str
    target_id: str
    initiator_items_to_target: List[str] # ID предметов, котоыре ушли от инициатора
    target_items_to_initiator: List[str] # ID предметов, которые ушли от цели
    
@dataclass
class TradeCancelled(DomainEvent):
    trade_id: str
    cancelled_by: str
    reason: str