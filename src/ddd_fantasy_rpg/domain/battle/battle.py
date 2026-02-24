from typing import Dict, Optional


from ..shared.skill import SkillType
from ..common.random_provider import RandomProvider
from .combatant import Combatant, CombatantType

from ..common.exceptions import (
    CombatantNotAliveError,
    CombatantNotInBattleError,
    NotYourTurnError,
    BattleAlreadyFinishedError,
)

from .battle_result import BattleResult, BattleParticipant, PvpVictory, PlayerVictory, MonsterVictory
from .battle_action import BattleAction, BattleActionType
from .battle_action_result import AttackResult, FleeResult, SkillUseResult, ItemUseResult, BattleActionResult

class Battle:
    def __init__(self, attacker: Combatant, defender: Combatant):
        if not attacker.is_alive or not defender.is_alive:
            raise CombatantNotAliveError()
        self._attacker = attacker
        self._defender = defender
        self._current_turn_owner_id = attacker.id
        self._is_finished = False
        self._winner: Optional[Combatant] = None
        self._flee_attempts: Dict[str, int] = {attacker.id: 0, defender.id: 0}

    @property
    def is_finished(self) -> bool:
        return self._is_finished

    @property
    def winner(self) -> Optional[Combatant]:
        return self._winner

    def _end_battle(self, winner: Combatant) -> None:
        self._is_finished = True
        self._winner = winner

    def _calculate_base_damage(self, attacker: Combatant) -> int:
        # Урон = сила
        base = attacker.stats.strength
        return base

    def _is_critical_hit(self, attacker: Combatant, defender: Combatant, randome_provider: RandomProvider) -> bool:
        # Шанс крита = (ловкость атакующего) / (ловкость защищающегося + 10)
        crit_chance = attacker.stats.agility / (defender.stats.agility + 10)

        # TODO: увеличить шанс крита
        return randome_provider.random() < min(crit_chance, 0)  # макс 50%

    def _can_flee(self, fleeing: Combatant, opponent: Combatant, randome_provider: RandomProvider) -> bool:
        # шас побега растет с каждой попыткой
        attemps = self._flee_attempts[fleeing.id]
        base_chance = 0.3 + (attemps * 0.2)  # 30% 40% 70%
        agility_factor = fleeing.stats.agility / (opponent.stats.agility + 1)
        total_chance = min(base_chance * agility_factor, 0.9)
        success = randome_provider.random() < total_chance
        if success:
            return True
        else:
            self._flee_attempts[fleeing.id] += 1
            return False

    def _advance_turn(self, next_combatant: Combatant) -> None:
        """Передаем ход следующему игроку и уменьшает кулдауны."""
        if not self.is_finished:
            self._current_turn_owner_id = next_combatant.id
            next_combatant._reduce_colldowns()

    def _perform_attack(
        self,
        actor: Combatant,
        opponent: Combatant,
        random_provider: RandomProvider
    ) -> AttackResult:
        damage = self._calculate_base_damage(actor)
        is_critical = self._is_critical_hit(actor, opponent, random_provider)

        if is_critical:
            # TODO: добавить множитель крита
            pass

        opponent._take_damage(damage)

        # Проверка смерти
        if not opponent.is_alive:
            self._end_battle(actor)

        # Передать ход
        self._advance_turn(opponent)
        return AttackResult(
            action_type=BattleActionType.ATTACK,
            success=True,
            damage=damage,
            is_critical=is_critical,
            details="Critical hit!" if is_critical else ""
        )

    def _perform_flee(
        self,
        actor: Combatant,
        opponent: Combatant,
        randome_provider: RandomProvider
    ) -> FleeResult:

        can_flee = self._can_flee(actor, opponent, randome_provider)
        if can_flee:
            self._end_battle(opponent)  # победитель - оставшийся
            self._current_turn_owner_id = None
            return FleeResult(
                action_type=BattleActionType.FLEE,
                success=True,
                details="Flee successfully!"
            )
        else:
            self._flee_attempts[actor.id] += 1
            self._advance_turn(opponent)
            return FleeResult(
                action_type=BattleActionType.FLEE,
                success=False,
                details="Failed to flee!"
            )

    def _perform_skill_use(
        self,
        actor: Combatant,
        opponent: Combatant,
        skill_name: str,
    ) -> SkillUseResult:
        try:
            effect = actor._use_skill(skill_name)
            skill = effect["skill"]
            value = effect['effect_value']

            if skill.skill_type == SkillType.DAMAGE:
                opponent._take_damage(value)
                return SkillUseResult(
                    action_type=BattleActionType.USE_SKILL,
                    success=True,
                    skill_name=skill_name,
                    damage=value,
                    heal=None,
                    details=f"Used {skill.name} for {value} damage"
                )
            elif skill.skill_type == SkillType.HEAL:
                actor._current_hp = min(actor.stats.max_hp, actor._current_hp + value)
                return SkillUseResult(
                    action_type=BattleActionType.USE_SKILL,
                    success=True,
                    skill_name=skill_name,
                    damage=None,
                    heal=value,
                    details=f"Used {skill.name} and healed for {value} HP!"
                )
            else:
                print("Должны быть другие эффеты")
                return SkillUseResult(
                    action_type=BattleActionType.USE_SKILL,
                    success=False,
                    skill_name=skill_name,
                    damage=None,
                    heal=None,
                    details=f"Произошла ошибка при использовании {skill_name}"
                ) 
        except ValueError as e:
            raise ValueError("Сработал неизвестный скилл")
    
    def _perform_item_use(
        self,
        actor: Combatant,
        opponent: Combatant,
        item_name: str,
    ) -> ItemUseResult:
        # добавить реализацию
        return ItemUseResult(
            action_type=BattleActionType.USE_ITEM,
            success=True,
            item_name=item_name,
            daetails=f"Испрользован пердмет {item_name}"
        )
    
    
    def is_pvp(self) -> bool:
        """Проверяет, является ли бой PVP (игрок VS игрок)."""
        return (
            self._attacker.combatant_type == CombatantType.PLAYER and
            self._defender.combatant_type == CombatantType.PLAYER
        )

    def get_opponent_id(self, combatant_id: str) -> Combatant:
        """Возвращает ID противника для данного бойца."""
        if self._attacker.id == combatant_id:
            return self._defender
        elif self._defender.id == combatant_id:
            return self._attacker
        else:
            raise CombatantNotInBattleError()

    def get_combatant_by_id(self, combatant_id: str) -> Combatant:
        if self._attacker.id == combatant_id:
            return self._attacker
        elif self._defender.id == combatant_id:
            return self._defender
        else:
            raise CombatantNotInBattleError()

    def perform_action(
        self,
        acting_combatant_id: str,
        action: BattleAction,
        random_provider: RandomProvider
    ) -> BattleActionResult:
        if self._is_finished:
            raise BattleAlreadyFinishedError()

        if acting_combatant_id != self._current_turn_owner_id:
            raise NotYourTurnError()

        actor = self.get_combatant_by_id(acting_combatant_id)
        opponent = self._defender if actor.id == self._attacker.id else self._attacker

        if action.action_type == BattleActionType.ATTACK:
            return self._perform_attack(actor, opponent, random_provider)

        elif action.action_type == BattleActionType.FLEE:
            return self._perform_flee(actor, opponent, random_provider)

        elif action.action_type == BattleActionType.USE_SKILL:
            if not action.skill_name:
                raise ValueError("Skill name is required")
            return self._perform_skill_use(actor, opponent, action.skill_name)

        elif action.action_type == BattleActionType.USE_ITEM:
            if not action.item_name:
                raise ValueError("Item ID is required")
            return self._perform_item_use(actor, opponent, action.item_name)

        else:
            raise ValueError(f"Unsupported action type: {action.action_type}")

    def get_battle_result(self) -> BattleResult:
        """Возвращает результат завершенного боя."""

        if not self.is_finished:
            raise ValueError("Battle is not finished")

        winner = self.winner
        loser = self.get_opponent_id(winner.id)

        winner_participant = BattleParticipant(
            id=winner.id,
            is_player=winner.is_player,
            is_monster=winner.is_monster
        )

        loser_participant = BattleParticipant(
            id=loser.id,
            is_player=loser.is_player,
            is_monster=loser.is_monster
        )

        is_pvp = winner.is_player and loser.is_player

        # определяем тип исхода
        if is_pvp:
            outcome = PvpVictory(
                winner=winner_participant,
                loser=loser_participant,
                loot=[]
            )
        elif winner.is_player:
            outcome = PlayerVictory(
                winner=winner_participant,
                loser=loser_participant,
                loot=[],
                experience_gained=0
            )
        else:  # winner.is_monster
            outcome = MonsterVictory(
                winner=winner_participant,
                loser=loser_participant
            )

        return BattleResult(outcome=outcome, is_pvp=is_pvp)
