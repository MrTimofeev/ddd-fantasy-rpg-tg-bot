from ddd_fantasy_rpg.domain.battle.battle_action_result import AttackResult, SkillUseResult,FleeResult, ItemUseResult
from ddd_fantasy_rpg.application.use_cases.perform_battle_action import BattleTurnResult

class BattleMessageFormatter:
    def format_turn(self, turn: BattleTurnResult) -> str:
        hp_section = self._format_hp_section(
            turn.player_hp,
            turn.opponent_name,
            turn.opponent_hp,
            turn.is_opponent_player
        )
        action_section = self._format_action(turn.action_result, turn.is_opponent_player)
        return f"{hp_section}\n\n{action_section}"
    
    def _format_hp_section(self, player_hp, opponent_name, opponent_hp, is_opponent_player):
        label = "Игрока" if is_opponent_player else "Монстра"
        return f"❤️ Твоё HP: {player_hp}\n👹 HP {label.lower()}: {opponent_hp}"
    
    def _format_action(self, action_result, is_opponent_player):
        if not action_result.success:
            return f"❌ {action_result.details}"
        
        if isinstance(action_result, AttackResult):
            target = "противника" if is_opponent_player else "монстра"
            crit = " (КРИТ!)" if action_result.is_critical else ""
            return f"💥 Нанесено {action_result.damage} урона {target}!{crit}"
        
        elif isinstance(action_result, SkillUseResult):
            return f"✨ {action_result.details}"
        
        elif isinstance(action_result, FleeResult):
            return "🏃 Ты сбежал!"
        
        elif isinstance(action_result, ItemUseResult):
            return f"🧪 {action_result.daetails}" 
        
        return "Неизвестное действие"