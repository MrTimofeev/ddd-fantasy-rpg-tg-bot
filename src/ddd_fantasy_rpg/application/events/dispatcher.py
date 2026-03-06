from abc import ABC, abstractmethod
from typing import Type, Dict, List, Any, TypeVar

from ddd_fantasy_rpg.domain.common.domain_event import DomainEvent

T = TypeVar('T', bound=DomainEvent)

class EventHandler(ABC):
    """
    Базовый класс для всех обработчиков собыйти.
    Каждый конкретный хендлер должен наследоваться от этого класса
    и указываьт, каое событие он обрабатывает.
    """
    
    @property
    @abstractmethod
    def subscribed_to(self) -> Type[DomainEvent]:
        """Возвращает класс события, на которое подписан этот хендлер"""
        raise NotImplementedError
    
    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """Логика обработки события."""
        pass
    
class EventDispatcher:
    """
    Шина событий. Регистрирует хендлеры и распределяет события по ним.
    """
    
    def __init__(self):
        # Словарь: КлассСобытия -> Список Хендлеров
        self._handler: Dict[Type[DomainEvent], List[EventHandler]] = {}
        
    def register(self, handler: EventHandler) -> None:
        """
        Геристрирует обработчик в шине.
        """
        event_type = handler.subscribed_to
        
        if event_type not in self._handler:
            self._handler[event_type] = []
            
        self._handler[event_type].append(handler)
        print(f"[EventDispatcher] Handler {handler.__class__.__name__} registered {event_type.__name__}")
    
    async def publish(self, events: List[DomainEvent]) -> None:
        """
        Публикует список событий.
        Для каждого события находит всех подписчиков и вызыват их асинхронно.
        """
        
        for event in events:
            event_type = type(event)
            
            # Находим всех подписчиков на это событие
            # Также проверяем родителей класса (на слуйча если хендлер подписан на базовый DomainEvent)
            subscribers = self._handler.get(event_type, [])
            
            if not subscribers:
                print(f"[EventDispatcher] No listeners for {event_type.__name__}")
                continue
            
            # Запускаем всех подписчиков параллельно
            import asyncio
            await asyncio.gather(
                *[handler.handle(event) for handler in subscribers],
                return_exceptions=True # Если один хендлер упадет, остальные продолжат работу
            )
        
    
    