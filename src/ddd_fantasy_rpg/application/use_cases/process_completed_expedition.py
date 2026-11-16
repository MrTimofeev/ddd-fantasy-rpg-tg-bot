from typing import Callable

from ddd_fantasy_rpg.domain.expedition.expedition_event import MonsterEncounter, PlayerDuelEncounter
from ddd_fantasy_rpg.domain.expedition.expedition import Expedition
from ddd_fantasy_rpg.domain.common.time_provider import TimeProvider
from ddd_fantasy_rpg.domain.common.random_provider import RandomProvider
from ddd_fantasy_rpg.domain.common.unit_of_work import UnitOfWork
from ddd_fantasy_rpg.application.use_cases.start_battle import StartBattleUseCase
from ddd_fantasy_rpg.domain.player.exceptions import PlayerNotFoundError


class ProcessCompletedExpeditionUseCase:
    """
    Use Case для запуска событий у завершенных экспедиций
    """

    def __init__(
        self,
        start_battle_use_case: StartBattleUseCase,
        time_provider: TimeProvider,
        random_provider: RandomProvider,
        uow_factory: Callable[[], UnitOfWork],
    ):
        self._start_battle_uc = start_battle_use_case
        self._time_provider = time_provider
        self._random_provider = random_provider
        self._uow_factory = uow_factory

    async def execute(self, expedition: Expedition):
        async with self._uow_factory() as uow:
            player = await uow.players.get_by_id(expedition.player_id)
            if not player:
                raise PlayerNotFoundError(expedition.player_id)

            if isinstance(expedition.outcome, MonsterEncounter):
                await self._start_battle_uc.start_pve_battle(player, expedition.outcome.monster)
            elif isinstance(expedition.outcome, PlayerDuelEncounter):
                if not expedition.outcome.opponent_player_id:
                    raise ValueError(
                        "Игроку не нашло пару сделай генерацию другого события")
                await self._start_battle_uc.start_pvp_battle(expedition.player_id, expedition.outcome.opponent_player_id)
            # TODO: добавить добычу ресурсов и торговца
            
            expedition.set_start_event_status(expedition.outcome)

            await uow.expeditions.save(expedition)
