from typing import Optional

from ddd_fantasy_rpg.domain.random_provider import RandomProvider
from ddd_fantasy_rpg.domain.battle import Battle, BattleAction, BattleActionType, CombatantType
from ddd_fantasy_rpg.domain.repositories.battle_repository import BattleRepository
from ddd_fantasy_rpg.application.use_cases.complete_battle import CompleteBattleUseCase


class BattleActionResult:
    """Результат выполнения действия в бою."""
    def __init__(
        self, 
        message: str,
        is_finished: bool = False,
        battle_outcome: Optional[dict] = None,
        requires_opponent_notification: bool = False,
        opponent_id: Optional[tuple] = None
    ):
        self.message = message
        self.is_finished = is_finished
        self.battle_outcome = battle_outcome
        self.requires_opponent_notification = requires_opponent_notification
        self.opponent_id = opponent_id
        
class PerformBattleActionUseCase:
    """
    Use case для выполнения действия игрока в бою.
    Обрабатывает PVE (игрок vs монстр) и PVP (игрок vs игрок).
    """
    
    def __init__(
        self,
        random_provider: RandomProvider,
        battle_repository: BattleRepository,
        complete_battle_use_case: CompleteBattleUseCase,
    ):
        self._random_provider = random_provider
        self._battle_repo = battle_repository
        self._complete_buttle_uc = complete_battle_use_case
        
    async def execute(self, player_id: str, action: BattleAction) -> BattleActionResult:
        """
        Выполняет действие игрока в бою и возвращает результат.
        Для PvE автоматически выполняет ход монстра.
        Для PVP только регистрирует ход игрока.
        """
        # 1. Получаем активный бой
        battle = await self._battle_repo.get_active_battle_for_player(player_id)
        if not battle:
            raise ValueError("Active battle not found for player")
        
        # 2. Проверяем, что бой еще не завершен
        if battle.is_finished:
            raise ValueError("Battle is already finisjed")
        
        # 3. Выпоолняем действие игрока
        result = battle.perform_action(player_id, action, self._random_provider)
        
        # 4. Если бой завершился после хода игрока
        if battle.is_finished:
            outcome = await self._complete_buttle_uc.execute(battle)
            await self._battle_repo.save(battle)
            message = self._format_battle_result(result, battle, player_id)
            return BattleActionResult(
                message=message,
                is_finished=True,
                battle_outcome=outcome,
                opponent_id=(battle.get_opponent_id(player_id).id, battle.get_opponent_id(player_id).combatant_type)
            )
            
        # 5. Определяем тип боя
        is_pvp = battle.is_pvp()
        
        # 6. Для PvE: монстр автоматически атакует
        if not is_pvp:
            opponent_id = battle.get_opponent_id(player_id)
            monster_action = BattleAction(action_type=BattleActionType.ATTACK)
            monster_result = battle.perform_action(opponent_id.id, monster_action, self._random_provider)
            
            # Формируем сообщение с ходом монстра
            message = self._format_battle_result(result, battle, player_id)
            if monster_result.get("success", False):
                message += f"\n\n👹 Монстр атакует!\n💥 Нанесено {monster_result.get('damage', 0)} урона."
            else:
                message += f"\n\n👹 Монстр пытается атаковать, но промахивается!"
                
            # Проверяем, завершился ли бой после хода монстра
            if battle.is_finished:
                outcome = await self._complete_buttle_uc.execute(battle)
                await self._battle_repo.save(battle)
                return BattleActionResult(
                    message=message, 
                    is_finished=True,
                    battle_outcome=outcome
                )
            
            # Сохраняем промежуточное состояние
            await self._battle_repo.save(battle)
            return BattleActionResult(message=message)
        
        # 7. Для PVP: сохраняем состояние и уведомляем противника
        else:
            opponent_id = battle.get_opponent_id(player_id)
            await self._battle_repo.save(battle)
            message = self._format_battle_result(result, battle, player_id)
            return BattleActionResult(
                message=message,
                requires_opponent_notification=True,
                opponent_id=(battle.get_opponent_id(player_id).id, battle.get_opponent_id(player_id).combatant_type)
            )
    
    def _format_battle_result(self, result: dict, battle: Battle, player_id: str) -> str:
        """Форматирует результат действия для игрока."""
        # Получаем HP игрока и противника
        player_combatant = battle.get_combatant_by_id(player_id)
        opponent_combatant = battle.get_opponent_id(player_id)
        
        player_hp = player_combatant.current_hp
        opponent_hp = opponent_combatant.current_hp
        
        # Определеяем тип противника
        opponent_label = "Игрока" if opponent_combatant.combatant_type == CombatantType.PLAYER else "Монстра"
        
        msg = f"❤️ Твоё HP: {player_hp}\n"
        msg += f"👹 HP {opponent_label.lower()}: {opponent_hp}\n\n"
        
        if result["success"]:
            if result["action"] == "attack":
                target = "противника" if opponent_combatant.combatant_type == CombatantType.PLAYER else "монстра"
                msg += f"💥 Нанесено {result.get('damage', 0)} урона {target}!"
            elif result["action"] == "flee":
                msg += "🏃 Ты сбежал!"
            elif result["action"] == "use_skill":
                msg += f"✨ {result.get('details', 'Использован скилл')}"
            elif result["action"] == "use_item":
                msg += f"🧪 Использован предмет: +{result.get('heal', 0)} HP"
        else:
            msg += f"❌ {result['details']}"
        
        return msg
            
            
        