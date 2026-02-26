from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict

from ddd_fantasy_rpg.domain.shared.skill import Skill, SkillType
from ddd_fantasy_rpg.domain.shared.exeptions import SkillNotAvailableError, SkillOnCooldownError

class CombatantType(Enum):
    PLAYER = "player"
    MONSTER = "monster"


@dataclass(frozen=True)
class CombatantStats:
    strength: int
    agility: int
    intelligence: int
    max_hp: int


@dataclass
class Combatant:
    id: str
    name: str
    combatant_type: CombatantType
    stats: CombatantStats
    skills: List[Skill] = field(default_factory=list)
    _current_hp: int = field(default=None)
    _skill_cooldowns: Dict[str, int] = field(init=False, default_factory=dict)

    def __post_init__(self):
        # Если HP не задан - используем max_hp
        if self._current_hp is None:
            self._current_hp = self.stats.max_hp

        # Ограничиваем HP диапозоном [0, max_hp]
        if self._current_hp > self.stats.max_hp:
            self._current_hp = self.stats.max_hp
        if self.current_hp < 0:
            self._current_hp = 0

        self._skill_cooldowns = {skill.name: 0 for skill in self.skills}

    @property
    def current_hp(self):
        return self._current_hp

    @property
    def is_alive(self) -> bool:
        return self.current_hp > 0

    @property
    def available_skills(self) -> List[Skill]:
        return [s for s in self.skills if self._skill_cooldowns[s.name] == 0]

    @property
    def is_player(self) -> bool:
        return self.combatant_type == CombatantType.PLAYER

    @property
    def is_monster(self) -> bool:
        return self.combatant_type == CombatantType.MONSTER

    def _take_damage(self, damage: int) -> None:
        self._current_hp = max(0, self._current_hp - damage)

    def _use_skill(self, skill_name: str) -> dict:
        if skill_name not in self._skill_cooldowns:
            raise SkillNotAvailableError(skill_name)
        if self._skill_cooldowns[skill_name] > 0:
            raise SkillOnCooldownError(skill_name)

        skill = next(s for s in self.skills if s.name == skill_name)
        self._skill_cooldowns[skill_name] = skill.cooldown_turns
        return {
            "skill": skill,
            "effect_value": self._calculate_skill_effect(skill)
        }

    def _calculate_skill_effect(self, skill: Skill) -> int:
        if skill.skill_type == SkillType.DAMAGE:
            stat = self.stats.intelligence if self.combatant_type == CombatantType.PLAYER else self.stats.strength
            return skill.base_power + stat
        elif skill.skill_type == SkillType.HEAL:
            return skill.base_power + self.stats.intelligence
        else:
            return skill.base_power  # для BUFF и прочих

    def _reduce_colldowns(self) -> None:
        """Уменьшает все активные coldown'ы на 1"""
        for name in self._skill_cooldowns:
            if self._skill_cooldowns[name] > 0:
                self._skill_cooldowns[name] -= 1

