from ddd_fantasy_rpg.domain.expedition import ExpeditionEvent, MonsterEncounter, ExpeditionStatus
from ddd_fantasy_rpg.domain.time_provider import TimeProvider
from ddd_fantasy_rpg.domain.random_provider import RandomProvider
from ddd_fantasy_rpg.domain.repositories.expedition_repository import ExpeditionRepository
from ddd_fantasy_rpg.domain.repositories.player_repository import PlayerRepository
from ddd_fantasy_rpg.domain.expedition_event_generator import generate_event_for_expedition
from ddd_fantasy_rpg.application.use_cases.start_battle import StartBattleUseCase


class CompleteExpeditionUseCase:
    """
    Use Case для завершения экспедиции.
    """
    def __init__(
        self,
        expedition_repository: ExpeditionRepository,
        player_repository: PlayerRepository,
        start_battle_use_case: StartBattleUseCase,
        time_provider: TimeProvider,
        random_provider: RandomProvider,
    ):
        self._expedition_repo = expedition_repository
        self._player_repo = player_repository
        self._start_battle_uc = start_battle_use_case
        self._time_provider = time_provider
        self._random_provider = random_provider

    async def execute(self, player_id: str) -> ExpeditionEvent:
        # 1. Получаем активную вылазку
        expedition = await self._expedition_repo.get_by_player_id(player_id)
        if not expedition:
            raise ValueError("No active expedition found")
        if not expedition.is_finished(self._time_provider):
            raise ValueError("Expedition is not finished yet")

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
            await self._start_battle_uc.execute(player_id, event.monster)

        # 4. Сохраняем результат вылазки
        expedition.complete_with_event(event=event)

        await self._expedition_repo.save(expedition)

        return event
