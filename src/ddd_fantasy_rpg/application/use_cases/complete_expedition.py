from ddd_fantasy_rpg.domain.expedition import MonsterEncounter, PlayerDuelEncounter
from ddd_fantasy_rpg.domain.common.time_provider import TimeProvider
from ddd_fantasy_rpg.domain.common.random_provider import RandomProvider
from ddd_fantasy_rpg.domain.common.unit_of_work import UnitOfWork
from ddd_fantasy_rpg.application.use_cases.start_battle import StartBattleUseCase
from ddd_fantasy_rpg.domain.expedition import ExpeditionNotFoundError, ExpeditionNotFinishedError


class CompleteExpeditionUseCase:
    """
    Use Case для завершения экспедиции и запуска заранее сгенерированного события
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

    async def execute(self, player_id: str, uow: UnitOfWork):
        # 1. Получаем активную вылазку
        expedition = await uow.expeditions.get_by_player_id(player_id)
        if not expedition:
            raise ExpeditionNotFoundError(player_id)
        if not expedition.is_finished(self._time_provider):
            raise ExpeditionNotFinishedError()

        # TODO: здесь будет либо монстр либо торговец либо ресы добывать
        # 3. Если монстр - запускаем бой
        if isinstance(expedition.outcome, MonsterEncounter):
            await self._start_battle_uc.start_pve_battle(player_id, expedition.outcome.monster, uow)
        # 3. Если pvp и нашелся противник - запускаем бой
        elif isinstance(expedition.outcome, PlayerDuelEncounter):
            if not expedition.outcome.opponent_player_id:
                # пока выбрасываем исключение но позже генерируем другое событие
                raise ValueError(
                    "Игроку не нашло пару сделай генерацию другого события")
            await self._start_battle_uc.start_pvp_battle(player_id, expedition.outcome.opponent_player_id, uow)
