from ddd_fantasy_rpg.domain.expedition import ExpeditionEvent, MonsterEncounter, ExpeditionStatus
from ddd_fantasy_rpg.domain.common.time_provider import TimeProvider
from ddd_fantasy_rpg.domain.common.random_provider import RandomProvider
from ddd_fantasy_rpg.domain.common.unit_of_work import UnitOfWork
from ddd_fantasy_rpg.domain.expedition.expedition_event_generator import generate_event_for_expedition
from ddd_fantasy_rpg.application.use_cases.start_battle import StartBattleUseCase
from ddd_fantasy_rpg.domain.common.exceptions import ExpeditionNotFoundError, ExpeditionNotFinishedError


class CompleteExpeditionUseCase:
    """
    Use Case для завершения экспедиции.
    """

    def __init__(
        self,
        start_battle_use_case: StartBattleUseCase,
        time_provider: TimeProvider,
        random_provider: RandomProvider,
    ):
        self._start_battle_uc = start_battle_use_case
        self._time_provider = time_provider
        self._random_provider = random_provider

    async def execute(self, player_id: str, uow: UnitOfWork) -> ExpeditionEvent:
        # 1. Получаем активную вылазку
        expedition = await uow.expeditions.get_by_player_id(player_id)
        if not expedition:
            raise ExpeditionNotFoundError(player_id)
        if not expedition.is_finished(self._time_provider):
            raise ExpeditionNotFinishedError()

        if expedition.status == ExpeditionStatus.INTERRUPTED:
            # Уже есьт событие дуэли
            return expedition.outcome

        # 2. Генерируем событие
        event = generate_event_for_expedition(
            distance=expedition.distance,
            random_provider=self._random_provider
        )

        # 3. Если монстр - запускаем бой
        if isinstance(event, MonsterEncounter):
            # TODO: здесь будет либо монстр либо торговец либо ресы добывать
            await self._start_battle_uc.start_pve_battle(player_id, event.monster, uow)

        # 4. Сохраняем результат вылазки
        expedition.complete_with_event(event=event)

        await uow.expeditions.save(expedition)

        return event
