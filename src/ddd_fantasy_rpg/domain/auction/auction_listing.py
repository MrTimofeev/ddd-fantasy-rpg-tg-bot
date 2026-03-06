from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum

from ddd_fantasy_rpg.domain.items.item_instance import ItemInstance
from ddd_fantasy_rpg.domain.common.domain_event import DomainEvent
from ddd_fantasy_rpg.domain.auction.events import (
    AuctionListingCreated, 
    AuctionItemSold,
    AuctionListingExpired, 
    AuctionListingCancelled,
)

from ddd_fantasy_rpg.domain.player.exceptions import DomainError

class ListingStatus(Enum):
    ACTIVE = "active"
    SOLD = "sold"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    
@dataclass
class AuctionListing:
    """
    Агрегат лота аукциона.
    Отвечает за продажу предмета от одного игрока другому.
    """
    id: str
    seller_id: str
    item: ItemInstance
    price: int
    created_at: datetime
    duratoin_hours: int
    status: ListingStatus = ListingStatus.ACTIVE
    
    _buyer_id: Optional[str] = field(default=None, init=False)
    _pending_events: list[DomainEvent] = field(default_factory=list, repr=False)
    
    def __post_init__(self):
        if self.price <=0:
            raise DomainError("Цена должна быть больше нуля")
        if self.item.is_equipped:
            raise DomainError("Нельзя выставить экипированный предмет на аукцион")

        # Генерируем событие создания
        expires_at = self.created_at + timedelta(hours=self.duratoin_hours)
        self._pending_events.append(
            AuctionListingCreated(
                listing_id=self.id,
                seller_id=self.seller_id,
                item_id=self.item.id,
                item_name=self.item.name,
                price=self.price,
                expires_at_timestamp=expires_at.timestamp()
            ))
    
    @property
    def expires_at(self) -> datetime:
        return self.created_at + timedelta(hours=self.duratoin_hours)
    
    @property
    def is_active(self) -> bool:
        return self.status == ListingStatus.ACTIVE
    
    def buy(self, buyer_id: str, buyer_gold: int, current_time: datetime, commission_rate: float = 0.05) -> tuple[ItemInstance]:
        """
        Покупка лота.
        :param buyer_id: ID покупателя
        :param buyer_gold: Золото покупателя (для проверки)
        :param current_time: Текущее время
        :param commission_rate: Комиссия аукциона (по умолчанию 5%)
        :return: (Предмет, Сумма для продавца)
        """"""
        Покупка лота.
        
        """
        if not self.is_active:
            raise DomainError(f"Лот не активен. Статус: {self.status}")
        
        if current_time > self.expires_at:
            self._expire()
            raise DomainError("Срок действия лота истек")
        
        if buyer_id == self.seller_id:
            raise DomainError("Нельзя купить собственный лот")
        
        # Расчет комиссии
        commission = int(self.price * commission_rate)
        net_profit = self.price - commission
        
        if buyer_gold < self.price:
            raise DomainError("Недостаточно золота для покупки")
        
        # Фиксация покупки
        self.status = ListingStatus.SOLD
        self._buyer_id = buyer_id
        
        self._pending_events.append(AuctionItemSold(
            listing_id=self.id,
            seller_id=self.seller_id,
            buyer_id=buyer_id,
            item_id=self.item.id,
            item_name=self.item.name,
            sold_price=self.price,
            commission_fee=commission,
            net_profit=net_profit
        ))
        
        # Возвращаем предмет и сумму, которую нужно начислить продавцу
        # Важно: предмет все еще привязан к этом лоту, сервис должен забрать его отсюда
        return self.item, net_profit
    
    def cancel(self, current_time: datetime) -> None:
        """Отмена лота продавцом (возврат предмета)"""
        if not self.is_active:
            raise DomainError("Можно отметь только активный лот")
        
        if current_time > self.expires_at:
            self._expire()
            raise DomainError("Нельзя отменить истекший лот")
        
        self.status = ListingStatus.CANCELLED
        self._pending_events.append(AuctionListingCancelled(
            listing_id=self.id,
            seller_id=self.seller_id,
            item_id=self.item.id
        ))
        
    def check_expiration(self, current_time: datetime) -> bool:
        """Проверка истечения срока. Возвращает True если истек."""
        if self.is_active and current_time > self.expires_at:
            self._expire()
            return True
        return False
    
    def _expire(self) -> None:
        self.status = ListingStatus.EXPIRED
        self._pending_events.append(AuctionListingExpired(
            listing_id=self.id,
            seller_id=self.seller_id,
            item_id=self.item.id
        ))
        
    def pop_pending_events(self) -> list[DomainEvent]:
        events = list(self._pending_events)
        self._pending_events.clear()
        return events
    
    def __repr__(self) -> str:
        return f"AuctionListing(id={self.id}, seller={self.seller_id}, item={self.item.name}, price={self.price}, status={self.status})"
        
        
        
        
    