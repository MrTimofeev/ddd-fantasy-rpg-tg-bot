from typing import Optional, Callable
from dataclasses import dataclass

from ddd_fantasy_rpg.domain.battle.battle_action import BattleAction, BattleActionType
from ddd_fantasy_rpg.domain.battle.battle_result import BattleResult
from ddd_fantasy_rpg.domain.battle.battle_action_result import BattleActionResult
from ddd_fantasy_rpg.domain.battle.combatant import Combatant
from ddd_fantasy_rpg.domain.battle.exceptions import BattleNotFoundError, BattleAlreadyFinishedError

from ddd_fantasy_rpg.domain.common.unit_of_work import UnitOfWork
from ddd_fantasy_rpg.application.use_cases.complete_battle import CompleteBattleUseCase


@dataclass(frozen=True)
class BattleTurnResult:
    """Результат ходяа в бою"""
     
    # доменный результат действия
    player_action_result: BattleActionResult
    opponent_action_result: Optional[BattleActionResult]
    
    # Контекст боя
    player_hp: int
    opponent_name: str
    opponent_hp: int
    is_opponent_player: bool
    
    # Метаданные
    is_finished: bool = False
    battle_outcome: Optional[BattleResult] = None
    requires_opponent_notification: bool = False
    opponent_id: Optional[str] = None
  
class PerformBattleActionUseCase:
    """
    Use case для выполнения действия игрока в бою.
    Обрабатывает PVE (игрок vs монстр) и PVP (игрок vs игрок).
    """

    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        complete_battle_use_case: CompleteBattleUseCase,
    ):
        self._complete_buttle_uc = complete_battle_use_case
        self._uow_factory = uow_factory

    async def execute(self, player_id: str, action: BattleAction) -> BattleTurnResult:
        """
        Выполняет действие игрока в бою и возвращает результат.
        Для PvE автоматически выполняет ход монстра.
        Для PVP только регистрирует ход игрока.
        """
        async with self._uow_factory() as uow:
            battle = await uow.battles.get_active_battle_for_player(player_id)
            if not battle:
                raise BattleNotFoundError(player_id)

            if battle.is_finished:
                raise BattleAlreadyFinishedError()

            player_result = battle.perform_action(
                acting_combatant_id=player_id, 
                action=action, 
            )

            player_combatant = battle.get_combatant_by_id(player_id)
            opponent_combatant = battle.get_opponent(player_id)
            is_pvp = battle.is_pvp
            
            opponent_result = None
            outcome = None
            
            if battle.is_finished:
                 # Бой закончился сразу. Финализируем.
                # ВНИМАНИЕ: Здесь лучше вызвать логику финализации напрямую или через событие,
                # чтобы не передавать uow внутрь другого use case.
                # TODO: добавить событие и хендлер обработки этого события
                # Для примера оставим вызов, но помни про риск связности.
                if is_pvp:
                    outcome = await self._complete_buttle_uc.complete_pvp_battle(battle)
                else:
                    outcome = await self._complete_buttle_uc.complete_pve_battle(battle)
                
                await uow.battles.save(battle)
                
                return self._make_result(
                    player_result=player_result,
                    opponent_result=None,
                    player_hp=player_combatant.current_hp,
                    opponent=opponent_combatant,
                    is_pvp=is_pvp,
                    is_finished=True,
                    outcome=outcome
                )              
                
            if not is_pvp:
                monster_action = BattleAction(action_type=BattleActionType.ATTACK)
                opponent_result = battle.perform_action(
                    acting_combatant_id=opponent_combatant.id,
                    action=monster_action,
                )
                
                # Обновляем ссылки на комбатантов (HP могли измениться)
                player_combatant = battle.get_combatant_by_id(player_id)
                opponent_combatant = battle.get_opponent(player_id)
                
                if battle.is_finished:
                    if is_pvp:
                        outcome = await self._complete_buttle_uc.complete_pvp_battle(battle)
                    else:
                        outcome = await self._complete_buttle_uc.complete_pve_battle(battle)
                    
                    await uow.battles.save(battle)
                    
                    return self._make_result(
                        player_result=player_result,
                        opponent_result=opponent_result,
                        player_hp=player_combatant.current_hp,
                        opponent=opponent_combatant,
                        is_pvp=False,
                        is_finished=True,
                        outcome=outcome
                    )                  
                     
            # Сохраняем промежуточное состояние
            await uow.battles.save(battle)
            
            return self._make_result(
                    player_result=player_result,
                    opponent_result=opponent_result,
                    player_hp=player_combatant.current_hp,
                    opponent=opponent_combatant,
                    is_pvp=is_pvp,
                    is_finished=False,
                    outcome=None
                )
            
    def _make_result(
        self,
        player_result: BattleActionResult,
        opponent_result: Optional[BattleActionResult],
        player_hp: int,
        opponent: Combatant,
        is_pvp: bool,
        is_finished: bool,
        outcome: Optional[BattleResult]
    ) -> BattleTurnResult:
        return BattleTurnResult(
            player_action_result=player_result,
            opponent_action_result=opponent_result,
            player_hp=player_hp,
            opponent_name=opponent.name,
            opponent_hp=opponent.current_hp,
            is_opponent_player=is_pvp,
            is_finished=is_finished,
            battle_outcome=outcome,
            requires_opponent_notification=is_pvp and not is_finished,
            opponent_id=opponent.id
        )
    
            