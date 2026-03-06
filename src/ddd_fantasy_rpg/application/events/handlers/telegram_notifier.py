from typing import Type

from ddd_fantasy_rpg.application.events.dispatcher import EventHandler
from ddd_fantasy_rpg.domain.common.domain_event import DomainEvent
from ddd_fantasy_rpg.domain.common.unit_of_work import UnitOfWork
from ddd_fantasy_rpg.domain.player.events import PlayerDied, PlayerCreated

from ddd_fantasy_rpg.domain.common.notifications import NotificationService

class PlayerCreatedTelegramHandler(EventHandler):
    def __init__(self, notification_service: NotificationService, uow: UnitOfWork):
        self._uow = uow
        self._notification_service = notification_service 
        
    @property
    def subscribed_to(self) -> type[DomainEvent]:
        return PlayerCreated
    

    async def handle(self, event: PlayerCreated) -> None:
        player = await self._uow.players.get_by_id(event.player_id)
        if not player:
            raise ValueError(f"Игрок с {event.player_id} не был найден")
            
        
        await self._notification_service.notify_create_player(player)


class PlayerDeathTelegramHandler(EventHandler):
    def __init__(self, notification_service: NotificationService, uow: UnitOfWork):
        self._uow = uow
        self._notification_service = notification_service 
    
    @property
    def subscribed_to(self) -> type[DomainEvent]:
        return PlayerDied
    
    async def handle(self, event: PlayerDied) -> None:
        player = await self._uow.players.get_by_id(event.player_id)
        
        # Вот здесь должен быть вызов метода у у сервиса уведомлений о том что игрок погиб
        # TODO: нужен реализованный метод уведомления о поражении
        # грубо гворя что-то тип этого:
        # await self._notification_service.notify_about_death(player)
        
        

        