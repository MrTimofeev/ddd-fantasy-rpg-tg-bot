from typing import Union, Optional
from dataclasses import dataclass

from ddd_fantasy_rpg.domain.common.random_provider import RandomProvider
from ddd_fantasy_rpg.domain.battle.battle_action import BattleAction, BattleActionType
from ddd_fantasy_rpg.domain.battle.battle_result import BattleResult
from ddd_fantasy_rpg.domain.battle.battle_action_result import AttackResult, FleeResult, ItemUseResult, SkillUseResult
from ddd_fantasy_rpg.domain.battle.exeptions import BattleNotFoundError, BattleAlreadyFinishedError

from ddd_fantasy_rpg.domain.common.unit_of_work import UnitOfWork
from ddd_fantasy_rpg.application.use_cases.complete_battle import CompleteBattleUseCase

@dataclass(frozen=True)
class BattleTurnResult:
    """Результат ходяа в бою"""
     
    # доменный результат действия
    action_result: Union[AttackResult, FleeResult, ItemUseResult, SkillUseResult]
    
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
        random_provider: RandomProvider,
        complete_battle_use_case: CompleteBattleUseCase,
    ):
        self._random_provider = random_provider
        self._complete_buttle_uc = complete_battle_use_case

    async def execute(self, player_id: str, action: BattleAction, uow: UnitOfWork) -> BattleTurnResult:
        """
        Выполняет действие игрока в бою и возвращает результат.
        Для PvE автоматически выполняет ход монстра.
        Для PVP только регистрирует ход игрока.
        """
        # 1. Получаем активный бой
        battle = await uow.battles.get_active_battle_for_player(player_id)
        if not battle:
            raise BattleNotFoundError(player_id)

        # 2. Проверяем, что бой еще не завершен
        if battle.is_finished:
            raise BattleAlreadyFinishedError()

        # 3. Выполняем действие игрока
        result = battle.perform_action(
            acting_combatant_id=player_id, 
            action=action, 
            random_provider=self._random_provider
        )

        player_combatant = battle.get_combatant_by_id(player_id)
        opponent_combatant = battle.get_opponent_id(player_id)
        is_pvp = battle.is_pvp()
        
        # 4. Если бой завершился после хода игрока
        if battle.is_finished:
            if is_pvp:
                outcome = await self._complete_buttle_uc.complete_pvp_battle(battle, uow)
            else:
                outcome = await self._complete_buttle_uc.complete_pve_battle(battle, uow)
            
            await uow.battles.save(battle)
            
            return BattleTurnResult(
                action_result=result,
                player_hp=player_combatant.current_hp,
                opponent_name=opponent_combatant.name,
                opponent_hp=opponent_combatant.current_hp,
                is_opponent_player=is_pvp,
                is_finished=True,
                battle_outcome=outcome,
                opponent_id=opponent_combatant.id
            )
            
        # 5. Для PvE: монстр автоматически атакует
        if not is_pvp:
            monster_action = BattleAction(action_type=BattleActionType.ATTACK)
            monster_result = battle.perform_action(
                acting_combatant_id=opponent_combatant.id,
                action=monster_action,
                random_provider=self._random_provider
            )
            
            # Проверяем, завершился ли бой после хода монстра
            if battle.is_finished:
                outcome = await self._complete_buttle_uc.complete_pve_battle(battle, uow)
                await uow.battles.save(battle)
                
                return BattleTurnResult(
                    action_result=monster_result, #Последние действие - монстра
                    player_hp=player_combatant.current_hp,
                    opponent_name=opponent_combatant.name,
                    opponent_hp=opponent_combatant.current_hp,
                    is_opponent_player=False,
                    is_finished=True,
                    battle_outcome=outcome,
                    opponent_id=opponent_combatant.id
                )
                
            # Сохраняем промежуточное состояние
            await uow.battles.save(battle)
            
            return BattleTurnResult(
                action_result=result,
                player_hp=player_combatant.current_hp,
                opponent_name=opponent_combatant.name,
                opponent_hp=opponent_combatant.current_hp,
                is_opponent_player=False,
                is_finished=False,
                opponent_id=opponent_combatant.id
            )
            
        # 6. Для PvP: сохраняем состояние и уведомляем противника
        else:
            await uow.battles.save(battle)
            
            return BattleTurnResult(
                action_result=result,
                player_hp=player_combatant.current_hp,
                opponent_name=opponent_combatant.name,
                opponent_hp=opponent_combatant.current_hp,
                is_opponent_player=True,
                is_finished=False,
                requires_opponent_notification=True,
                opponent_id=opponent_combatant.id
            )