from typing import Tuple, Optional
from ...domain.battle.combatant import Combatant
from ...domain.skills.skill import Skill
from ...domain.skills.skill_type import SkillType
from ...domain.common.random_provider import RandomProvider

class BattleMechanicsService:
    def __init__(self, random_provider: RandomProvider):
        self._random_provider = random_provider

    # --- Основные вычисления ---
    def calculate_base_damage(self, attacker: Combatant) -> int:
        # Пример: базовый урон + 50% от силы
        return attacker.stats.damage + int(attacker.stats.strength * 0.5)

    def is_critical_hit(self, attacker: Combatant, defender: Combatant) -> bool:
        # Пример: шанс крита зависит от ловкости
        crit_chance = attacker.stats.agility / (defender.stats.agility + 10)
        roll = self._random_provider.random() # 0.0 to 1.0
        return roll < crit_chance

    def can_flee(self, fleeing: Combatant, opponent: Combatant, flee_attempts: int) -> bool:
        # Пример формулы
        base_chance = 0.3 - (flee_attempts * 0.2)
        agility_factor = fleeing.stats.agility / (opponent.stats.agility + 1)
        total_chance = min(max(base_chance * agility_factor, 0.05), 0.9) # Мин. 5%, макс. 90%
        roll = self._random_provider.random()
        return roll < total_chance

    # --- Вычисления для действий (возвращают результаты, не меняя состояние) ---
    def calculate_damage_and_crit(self, attacker: Combatant, defender: Combatant) -> Tuple[int, bool]:
        base_damage = self.calculate_base_damage(attacker)
        is_critical = self.is_critical_hit(attacker, defender)
        damage = base_damage if not is_critical else int(base_damage * 1.5)
        effective_damage = max(1, damage - defender.stats.armor)
        return effective_damage, is_critical

    def calculate_skill_effect(self, skill: Skill, caster: Combatant, target: Optional[Combatant] = None) -> Tuple[SkillType, int, Optional[str]]:
        effect_value = skill.base_power
        if skill.skill_type == SkillType.DAMAGE:
            stat_bonus = caster.stats.intelligence if caster.combatant_type == "PLAYER" else caster.stats.strength
            effect_value += int(stat_bonus * 0.3)
        elif skill.skill_type == SkillType.HEAL:
            stat_bonus = caster.stats.intelligence if caster.combatant_type == "PLAYER" else caster.stats.strength
            effect_value += int(stat_bonus * 0.2)

        return skill.skill_type, effect_value, None

    def calculate_flee_success(self, fleeing: Combatant, opponent: Combatant, flee_attempts: int) -> bool:
        return self.can_flee(fleeing, opponent, flee_attempts)
