from typing import Dict

from ddd_fantasy_rpg.domain.common.random_provider import RandomProvider
from ddd_fantasy_rpg.domain.skills import SkillType
from ddd_fantasy_rpg.domain.battle.combatant import Combatant
from ddd_fantasy_rpg.domain.battle.battle_action import BattleActionType
from ddd_fantasy_rpg.domain.battle.battle_action_result import (
    AttackResult, FleeResult, SkillUseResult, ItemUseResult
)
from ddd_fantasy_rpg.domain.skills.exceptions import SkillNotAvailableError, SkillOnCooldownError


class BattleMechanicsService:
    """Доменный сервис для боевой механики."""

    def __init__(self, random_provider: RandomProvider):
        self._random = random_provider

    def calculate_base_damage(self, attacker: Combatant) -> int:
        """Рассчитывает базовый урон."""
        # TODO: Сделать учет класса
        return attacker.stats.strength

    def is_critical_hit(self, attacker: Combatant, defender: Combatant) -> bool:
        """Проверяет, является ли удар критическим."""
        if defender.stats.agility + 10 == 0:
            return False    
    
        crit_chance = attacker.stats.agility / (defender.stats.agility + 10)
        return self._random.random() < min(crit_chance, 0.5)

    def can_flee(self, fleeing: Combatant, opponent: Combatant, flee_attempts: int) -> bool:
        """Проверяет, может ли боец сбежать."""
        base_chance = 0.3 + (flee_attempts * 0.2)
        agility_factor = fleeing.stats.agility / (opponent.stats.agility + 1)
        total_chance = min(base_chance * agility_factor, 0.9)
        return self._random.random() < total_chance

    def perform_attack(
        self,
        actor: Combatant,
        opponent: Combatant,
        flee_attempts: Dict[str, int]
    ) -> AttackResult:
        """Выполняет аттаку."""
        damage = self.calculate_base_damage(actor)
        is_critical = self.is_critical_hit(actor, opponent)

        if is_critical:
            damage = int(damage * 1.5)

        return AttackResult(
            action_type=BattleActionType.ATTACK,
            success=True,
            damage=damage,
            is_critical=is_critical,
            details="Critical hit!" if is_critical else ""
        )

    def perform_flee(
        self,
        actor: Combatant,
        opponent: Combatant,
        flee_attempts: Dict[str, int]
    ) -> FleeResult:
        """Выполняет попытку побега."""

        current_attempts = flee_attempts.get(actor.id, 0)
        can_flee = self.can_flee(actor, opponent, current_attempts)

        if can_flee:
            return FleeResult(
                action_type=BattleActionType.FLEE,
                success=True,
                details="Flee successfully!"
            )
        else:
            return FleeResult(
                action_type=BattleActionType.FLEE,
                success=False,
                details="Failed to flee!"
            )

    def perform_skill_use(
        self,
        actor: Combatant,
        skill_id: str
    ) -> SkillUseResult:
        """Выполняет использование скилла."""
        try:
            effect = actor.use_skill(skill_id)

            if effect.skill_type == SkillType.DAMAGE:
                return SkillUseResult(
                    action_type=BattleActionType.USE_SKILL,
                    success=True,
                    skill_name=effect.skill_name,
                    damage=effect.effect_value,
                    heal=None,
                    details=f"Used {effect.skill_name} for {effect.effect_value} damage"
                )
            elif effect.skill_type == SkillType.HEAL:
                return SkillUseResult(
                    action_type=BattleActionType.USE_SKILL,
                    success=True,
                    skill_name=effect.skill_name,
                    damage=None,
                    heal=effect.effect_value,
                    details=f"Used {effect.skill_name} and healed for {effect.effect_value} HP!"
                )
            else:
                return SkillUseResult(
                    action_type=BattleActionType.USE_SKILL,
                    success=False,
                    skill_name=effect.skill_name,
                    damage=None,
                    heal=None,
                    details=f"Unknown skill effect: {effect.skill_type.value}"
                )
        except (SkillOnCooldownError, SkillNotAvailableError) as e:
            return SkillUseResult(
                action_type=BattleActionType.USE_SKILL,
                success=False,
                skill_name=skill_name,
                damage=None,
                heal=None,
                details=str(e)
            )
            
    def perform_item_use(
        self,
        item_name: str
    ) -> ItemUseResult:
        """Выполняет использование предмета"""
        # TODO: Реализовать логику предметов
        return ItemUseResult(
            action_type=BattleActionType.USE_ITEM,
            success=True,
            item_name=item_name,
            details=f"Used item: {item_name}"
        )
