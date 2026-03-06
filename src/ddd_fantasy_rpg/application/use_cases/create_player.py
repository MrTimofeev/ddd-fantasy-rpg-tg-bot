from ddd_fantasy_rpg.domain.player.player import Player
from ddd_fantasy_rpg.domain.player.race import Race
from ddd_fantasy_rpg.domain.player.player_profession import PlayerClass
from ddd_fantasy_rpg.domain.player.exceptions import PlayerAlreadyExistingError
from ddd_fantasy_rpg.domain.common.unit_of_work import UnitOfWork
from ddd_fantasy_rpg.domain.player.stats_calculation_service import StatsCalculationService
from ddd_fantasy_rpg.application.events.dispatcher import EventDispatcher


class CreatePlayerUseCase:
    """
    Use Case для создания нового игрока.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        dispatcher: EventDispatcher,
        stats_service: StatsCalculationService,
    ) -> None:
        self._uow = uow
        self._dispatcher = dispatcher
        self._stats_service = stats_service

    async def execute(
        self,
        player_id: str,
        telegram_id: int,
        name: str,
        race: Race = Race.HUMAN,
        player_class: PlayerClass = PlayerClass.WARRIOR,
    ):
        """
        Создает нового игрока с заданными параметрами.
        """
        async with self._uow as uow:
            existing = await uow.players.get_by_id(player_id)
            if existing:
                raise PlayerAlreadyExistingError(player_id)

            base_stats = self._stats_service.calculate_base_stats(
                race, player_class)
            
            
            # TODO: Сделать нормыльный выбор персонажа
            player = Player(
                id=player_id,
                telegram_id=telegram_id,
                name=name,
                race=race,
                profession=player_class,
                level=1,
                exp=0,
                base_stats=base_stats
            )

            await uow.players.save(player)

            events_to_publish = player.pop_pending_events()

        if events_to_publish:
            await self._dispatcher.publish(events_to_publish)

        return player
