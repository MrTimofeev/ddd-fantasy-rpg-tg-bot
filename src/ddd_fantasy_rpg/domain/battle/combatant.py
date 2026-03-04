from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict

from ddd_fantasy_rpg.domain.skills.skill import Skill, SkillType
from ddd_fantasy_rpg.domain.player.character_stats import CharacterStats
from ddd_fantasy_rpg.domain.common.base_exceptions import DomainError


class CombatantType(Enum):
    PLAYER = "player"
    MONSTER = "monster"


@dataclass(frozen=True)
class SkillEffect:
    """Эфект от использования скилла."""
    skill_name: str
    effect_value: int
    skill_type: SkillType


@dataclass
class Combatant:
    id: str
    name: str
    combatant_type: CombatantType
    stats: CharacterStats
    skills: List[Skill] = field(default_factory=list)
    max_hp: int = field(default=None)
    _current_hp: int = field(init=False)
    _skill_cooldowns: Dict[str, int] = field(init=False, default_factory=dict)

    def __post_init__(self):
        if self.max_hp is None:
            object.__setattr__(self, 'max_hp', self.stats.max_hp)
        object.__setattr__(self, '_current_hp', self.max_hp)
        for skill in self.skills:
            self._skill_cooldowns[skill.name] = 0
            
    @property
    def current_hp(self):
        return self._current_hp

    @property
    def is_alive(self) -> bool:
        return self.current_hp > 0

    @property
    def available_skills(self) -> List[Skill]:
        return [s for s in self.skills if self._skill_cooldowns.get(s.name, 0) <= 0]
    
    @property
    def is_player(self) -> bool:
        return self.combatant_type == CombatantType.PLAYER

    @property
    def is_monster(self) -> bool:
        return self.combatant_type == CombatantType.MONSTER

    def take_damage(self, damage: int) -> None:
        if damage <= 0:
            return
        new_hp = self._current_hp - damage
        object.__setattr__(self, '_current_hp', max(0, new_hp))


    def take_heal(self, heal_amount: int) -> None:
        if heal_amount <= 0:
            return
        
        new_hp = self._current_hp + heal_amount
        object.__setattr__(self, '_current_hp', min(self.max_hp, new_hp))

    def use_skill(self, skill_name: str) -> SkillEffect:
        skill = next((s for s in self.skills if s.name == skill_name), None)
        if not skill:
            raise DomainError(f"Навык '{skill_name}' не найден для бойца '{self.id}'.")

        if self._skill_cooldowns.get(skill.name, 0) > 0:
            raise DomainError(f"Навык '{skill_name}' находится на перезарядке для бойца '{self.id}'.")
        
        effect_value = self._calculate_skill_effect(skill)
        effect = SkillEffect(skill_name=skill.name, effect_value=effect_value, skill_type=skill.skill_type)

        self._skill_cooldowns[skill.name] = skill.cooldown_turns

        return effect

    def reduce_colldowns(self) -> None:
        """Публичный метод для уменьшения кулдаунов."""
        for name in self._skill_cooldowns:
            if self._skill_cooldowns[name] > 0:
                self._skill_cooldowns[name] -= 1

    def _calculate_skill_effect(self, skill: Skill) -> int:
        base_effect = skill.base_power
        relevant_stat = self.stats.intelligence if self.combatant_type == CombatantType.PLAYER else self.stats.strength
        return base_effect + int(relevant_stat * 0.3) 
