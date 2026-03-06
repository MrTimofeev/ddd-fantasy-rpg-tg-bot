from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional, Set
from enum import Enum

from ddd_fantasy_rpg.domain.items.item_instance import ItemInstance
from ddd_fantasy_rpg.domain.common.domain_event import DomainEvent
from ddd_fantasy_rpg.domain.trade.events import (
    TradeSessionCreated,
    TradeOfferUpdated,
    TradeAccepted,
    TradeRevoked,
    TradeCompleted,
    TradeCancelled,
)

from ddd_fantasy_rpg.domain.common.base_exceptions import DomainError


class TradeStatus(Enum):
    PENDING = "pending"       # Ожидание подтверждения
    ACCEPTED_INITIATOR = "accepted_initiator" # Инициатор готов
    ACCEPTED_TARGET = "accepted_target"       # Цель готова
    READY = "ready"           # Оба готовы
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    
@dataclass
class TraderOffer: 
    player_id: str
    items_ids: List[str] = field(default_factory=list)
    

@dataclass
class TradeSession:
    """
    Агрегат Сессии обмена.
    Гарантирует атомарносьт обмена: предметы переходят только когда оба подтвердили.
    """
    id: str
    initiator_id: str
    target_id: str
    status: TradeStatus = TradeStatus.PENDING
    
    _initiator_offer: TraderOffer = field(default_factory=lambda: TraderOffer(player_id=""))
    _target_offer: TraderOffer = field(default_factory=lambda: TraderOffer(player_id=""))
    
    # Фглаги готовности
    _is_initiator_ready: bool = field(default=False, init=False)
    _is_target_ready: bool = field(default=False, init=False)
    
    _pending_events: List[DomainEvent] = field(default_factory=list, repr=False)
    
    def __post_init__(self):
        if self.initiator_id == self.target_id:
            raise DomainError("Нельзя создавать сессию с самим собой")
        
        # инициализируем офферы правильными ID
        self._initiator_offer.player_id = self.initiator_id
        self._target_offer.player_id = self.target_id
        
        self._pending_events.append(TradeSessionCreated(
            trade_id=self.id,
            initiator_id=self.initiator_id,
            target_id=self.target_id
        ))
        
    def add_offer(self, player_id: str, item_ids: List[str]) -> None:
        if self.status in [TradeStatus.CANCELLED, TradeStatus.COMPLETED]:
            raise DomainError("Нельзя изменить предложение в завершенной или отмененой сделке")
        
        if player_id == self.initiator_id:
            self._initiator_offer.items_ids = item_ids.copy()
            self._is_initiator_ready = False # Сброс готовности при изменнеия состава
        elif player_id == self.target_id:
            self._target_offer.items_ids = item_ids.copy()
            self._is_target_ready = False
        else:
            raise DomainError("Неверный ID игрока для этого трейда")
        
        self._pending_events.append(TradeOfferUpdated(
            traid_id=self.id,
            player_id=player_id,
            offered_item_ids=item_ids
        ))
        
    def accept(self, player_id: str) -> None:
        if self.status in [TradeStatus.COMPLETED, TradeStatus.CANCELLED]:
            raise DomainError("Сделка уже завершена или отменена")
        
        if player_id == self.initiator_id:
            self._is_initiator_ready = True
        elif player_id == self.target_id:
            self._is_target_ready = True
        else:
            raise DomainError("Неверный игрок")

        self._pending_events.append(TradeAccepted(
            trade_id=self.id,
            player_id=player_id
        ))
        
        self._check_complection()
        
    def revoke_acceptance(self, player_id: str) -> None:
        if self.status == TradeStatus.READY:
            # если сделака уже в статусе READY, отзыв сбарсывает ее обратно
            if player_id == self.initiator_id:
                self._is_initiator_ready = False
            elif player_id == self.target_id:
                self._is_target_ready = False
                
            self._pending_events.append(TradeRevoked(
                    trade_id=self.id,
                    player_id=player_id
                ))

    def cancel(self, player_id: str, reason: str = "User cancelled") -> None:
        if self.status in [TradeStatus.CANCELLED, TradeStatus.CANCELLED]:
            return
        
        self.status = TradeStatus.CANCELLED
        self._pending_events.append(TradeCancelled(
            trade_id=self.id,
            cancelled_by=player_id,
            reason=reason
        ))
        
    def _check_completion(self) -> None:
        if self._is_initiator_ready and self._is_target_ready:
            if not self._initiator_offer.items_ids and not self._target_offer.items_ids:
                return
            
            self.status = TradeStatus.COMPLETED
            self._pending_events.append(TradeCompleted(
                trade_id=self.id,
                initiator_id=self.initiator_id,
                target_id=self.target_id,
                initiator_items_to_target=self._initiator_offer.items_ids,
                target_items_to_initiator=self._target_offer.items_ids
            ))
    
    def get_offers(self) -> tuple[List[str], List[str]]:
        return self._initiator_offer.items_ids, self._target_offer.items_ids
    
    def pop_pending_events(self) -> List[DomainEvent]:
        events = list(self._pending_events)
        self._pending_events.clear()
        return events
    
    def __repr__(self) -> str:
        return f"TradeSession(id={self.id}, status={self.status}, init={self.initiator_id}, target={self.target_id})"
    
    
