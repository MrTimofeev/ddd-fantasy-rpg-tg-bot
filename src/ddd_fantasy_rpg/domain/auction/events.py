from dataclasses import dataclass
from typing import Optional

from ddd_fantasy_rpg.domain.common.domain_event import DomainEvent

@dataclass
class AuctionListingCreated(DomainEvent):
    listing_id: str
    seller_id: str
    item_id: str
    item_name: str
    price: int
    expires_at_timestamp: float
    
@dataclass
class AuctionListingExpired(DomainEvent):
    listing_id: str
    seller_id: str
    item_id: str

@dataclass
class AuctionItemSold(DomainEvent):
    listing_id: str
    seller_id: str
    buyer_id: str
    item_id: str
    item_name: str
    sold_price: int
    commission_fee: int # Коммиссия аукциона (если есть)
    net_profit: int # Сколько получит продавец
    
@dataclass
class AuctionListingCancelled(DomainEvent):
    listing_id: str
    seller_id: str
    item_id: str