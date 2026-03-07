from typing import Callable

from ddd_fantasy_rpg.domain.common.time_provider import TimeProvider
from ddd_fantasy_rpg.domain.common.unit_of_work import UnitOfWork
from ddd_fantasy_rpg.domain.expedition.expedition_factory import ExpeditionFactory

from ddd_fantasy_rpg.domain.player.exceptions import PlayerNotFoundError, PlayerAlreadyOnExpeditionError
from ddd_fantasy_rpg.domain.expedition.expedition_distance import ExpeditionDistance
from ddd_fantasy_rpg.application.events.dispatcher import EventDispatcher


class StartExpeditionUseCase:
    """
    Use Case для старта экспедиции.
    """

    def __init__(
        self,
        expedition_factory: ExpeditionFactory,
        dispatcher: EventDispatcher,
        time_provider: TimeProvider,
        uow_factory: Callable[[], UnitOfWork],

    ):
        self._expedition_factory = expedition_factory
        self._dispatcher = dispatcher
        self._time_provider = time_provider
        self._uow_factory = uow_factory

    async def execute(self, player_id: str, distance: ExpeditionDistance):
        async with self._uow_factory() as uow:
            player = await uow.players.get_by_id(player_id)
            if player is None:
                raise PlayerNotFoundError(player_id)

            if not player.is_alive:
                if not player.try_respawn(self._time_provider.now()):
                    raise ValueError(
                        "Вы мертвы. Дождитесь пока исчетет таймер воскрешения, чтобы начать экспедицию")

                await uow.players.save(player)

            active_expedition = await uow.expeditions.get_by_player_id(player_id)
            if active_expedition and not active_expedition.is_finished(self._time_provider.now()):
                raise PlayerAlreadyOnExpeditionError(player_id)

            expedition = self._expedition_factory.create_new_expedition(
                player_id=player_id,
                distance=distance,
            )

            await uow.expeditions.save(expedition)

            events_to_publish = expedition.pop_pending_events()

        if events_to_publish:
            await self._dispatcher.publish(events_to_publish)

        return expedition
