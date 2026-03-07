from typing import Callable

from ddd_fantasy_rpg.application.events.dispatcher import EventHandler
from ddd_fantasy_rpg.domain.common.domain_event import DomainEvent
from ddd_fantasy_rpg.domain.common.unit_of_work import UnitOfWork
from ddd_fantasy_rpg.domain.player.events import PlayerDied, PlayerCreated
from ddd_fantasy_rpg.domain.expedition.events import ExpeditionStarted, ExpeditionCompleted

from ddd_fantasy_rpg.domain.common.notifications import NotificationService


class PlayerCreatedTelegramHandler(EventHandler):
    def __init__(
        self,
        notification_service: NotificationService,
        uow_factory: Callable[[], UnitOfWork],
    ):
        self._uow_factory = uow_factory
        self._notification_service = notification_service

    @property
    def subscribed_to(self) -> type[DomainEvent]:
        return PlayerCreated

    async def handle(self, event: PlayerCreated) -> None:
        async with self._uow_factory() as uow:
            player = await uow.players.get_by_id(event.player_id)
            if not player:
                raise ValueError(f"Игрок с {event.player_id} не был найден")

            await self._notification_service.notify_create_player(player)


class PlayerDeathTelegramHandler(EventHandler):
    def __init__(
        self,
        notification_service: NotificationService,
        uow_factory: Callable[[], UnitOfWork],
    ):
        self._uow_factory = uow_factory
        self._notification_service = notification_service

    @property
    def subscribed_to(self) -> type[DomainEvent]:
        return PlayerDied

    async def handle(self, event: PlayerDied) -> None:
        async with self._uow_factory() as uow:
            player = await uow.players.get_by_id(event.player_id)

            # Вот здесь должен быть вызов метода у у сервиса уведомлений о том что игрок погиб
            # TODO: нужен реализованный метод уведомления о поражении
            # грубо гворя что-то тип этого:
            # await self._notification_service.notify_about_death(player)


class ExpeditionCreatedTelegramHandler(EventHandler):
    def __init__(
        self,
        notification_service: NotificationService,
        uow_factory: Callable[[], UnitOfWork],
    ):
        self._uow_factory = uow_factory
        self._notification_service = notification_service

    @property
    def subscribed_to(self) -> type[DomainEvent]:
        return ExpeditionStarted

    async def handle(self, event: ExpeditionStarted) -> None:
        async with self._uow_factory() as uow:
            expedition = await uow.expeditions.get_by_player_id(event.player_id)
            if not expedition:
                raise ValueError(
                    f"Экспедиция {event.expedition_id} игрока {event.player_id} не была найдена")

            await self._notification_service.notify_create_expedition(expedition)


class ExpeditionCompletedTelegramHandler(EventHandler):
    def __init__(
        self,
        notification_service: NotificationService,
        uow_factory: Callable[[], UnitOfWork],
    ):
        self._uow_factory = uow_factory
        self._notification_service = notification_service

    @property
    def subscribed_to(self) -> type[DomainEvent]:
        return ExpeditionCompleted

    async def handle(self, event: ExpeditionCompleted):
        async with self._uow_factory() as uow:
            expedition = await uow.expeditions.get_by_player_id(event.player_id)
            if not expedition:
                raise ValueError(
                    f"Экспедиция {event.expedition_id} игрока {event.player_id} не была найдена")

            await self._notification_service.notify_completed_expedition(expedition)
