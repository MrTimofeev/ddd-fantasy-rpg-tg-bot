from abc import ABC, abstractmethod
from typing import Optional, List

from ddd_fantasy_rpg.domain.trade.trade_session import TradeSession

class TradeRepository(ABC):
    @abstractmethod
    async def save(self, session: TradeSession) -> None:
        raise NotImplementedError
    
    @abstractmethod
    async def get_by_id(self, trade_id: str) -> Optional[TradeSession]:
        raise NotImplementedError
    
    @abstractmethod
    async def get_active_trade_for_player(self, player_id: str) -> Optional[TradeSession]:
        """Найти активную сделку, где игрок учавствует."""
        raise NotImplementedError
    
    @abstractmethod
    async def delete(self, trade_id: str) -> None:
        raise NotImplementedError