from abc import ABC, abstractmethod
from typing import Optional, List

from ddd_fantasy_rpg.domain.auction.auction_listing import AuctionListing

class AuctionRepository(ABC):
    @abstractmethod
    async def save(self, listing: AuctionListing) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_id(self, listing_id: str) -> Optional[AuctionListing]:
        raise NotImplementedError
    
    @abstractmethod
    async def get_active_listings(self, page: int = 0, page_size = 20) -> List[AuctionListing]:
        raise NotImplementedError
    
    @abstractmethod
    async def get_listing_by_seller(self, seller_id: str) -> List[AuctionListing]:
        raise NotImplementedError
    
    @abstractmethod
    async def delete(self, listing_id: str) -> None:
        raise NotImplementedError