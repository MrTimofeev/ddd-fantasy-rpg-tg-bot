from ddd_fantasy_rpg.domain.expedition import MonsterEncounter, PlayerDuelEncounter
from ddd_fantasy_rpg.domain.expedition import Expedition
from ddd_fantasy_rpg.domain.common.time_provider import TimeProvider
from ddd_fantasy_rpg.domain.common.random_provider import RandomProvider
from ddd_fantasy_rpg.domain.common.unit_of_work import UnitOfWork
from ddd_fantasy_rpg.application.use_cases.start_battle import StartBattleUseCase
from ddd_fantasy_rpg.domain.player import PlayerNotFoundError

class ProcessCompletedExpeditionUseCase:
    """
    Use Case для запуска событий у завершенных экспедиций
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


    async def execute(self, expedition: Expedition, uow: UnitOfWork):
        # TODO: здесь будет либо монстр либо торговец либо ресы добывать
        
        # 1. Получаем игрока из текущей экспедиции
        player = await uow.players.get_by_id(expedition.player_id)
        if not player:
            raise PlayerNotFoundError(expedition.player_id)
        
        # 3. Если монстр - запускаем бой
        if isinstance(expedition.outcome, MonsterEncounter):
            await self._start_battle_uc.start_pve_battle(player, expedition.outcome.monster, uow)
        # 3. Если pvp и нашелся противник - запускаем бой
        elif isinstance(expedition.outcome, PlayerDuelEncounter):
            if not expedition.outcome.opponent_player_id:
                # пока выбрасываем исключение но позже генерируем другое событие
                raise ValueError(
                    "Игроку не нашло пару сделай генерацию другого события")
            await self._start_battle_uc.start_pvp_battle(expedition.player_id, expedition.outcome.opponent_player_id, uow)

        # 4 обновляем статус экспедиции
        expedition.start_event(expedition.outcome)
        
        # 5. сохраняем статус экспедиции
        await uow.expeditions.save(expedition)