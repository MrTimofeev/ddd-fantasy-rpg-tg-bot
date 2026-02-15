from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, List
from random import random

from .skill import Skill, SkillType


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
    _skill_colldowns: Dict[str, int] = field(init=False, default_factory=dict)

    def __post_init__(self):
        # Если HP не задан - используем max_hp
        if self._current_hp is None:
            self._current_hp = self.stats.max_hp
        
        # Ограничиваем HP диапозоном [0, max_hp]
        if self._current_hp > self.stats.max_hp:
            self._current_hp = self.stats.max_hp
        if self.current_hp < 0:
            self._current_hp = 0

        self._skill_colldowns = {skill.name: 0 for skill in self.skills}
    
    @property
    def current_hp(self):
        return self._current_hp
    
    @property
    def is_alive(self) -> bool:
        return self.current_hp > 0

    @property
    def available_skills(self) -> List[Skill]:
        return [s for s in self.skills if self._skill_colldowns[s.name] == 0]

    def _take_damage(self, damage: int) -> None:
        self._current_hp = max(0, self._current_hp - damage)

    def _use_skill(self, skill_name: str) -> dict:
        if skill_name not in self._skill_colldowns:
            raise ValueError(
                f"Skill '{skill_name}' is not available to this combatant")
        if self._skill_colldowns[skill_name] > 0:
            raise ValueError(f"Skill '{skill_name}' is on cooldown")

        skill = next(s for s in self.skills if s.name == skill_name)
        self._skill_colldowns[skill_name] = skill.cooldown_turns
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
        for name in self._skill_colldowns:
            if self._skill_colldowns[name] > 0:
                self._skill_colldowns[name] -= 1


class BattleActionType(Enum):
    ATTACK = "attack"
    USE_SKILL = "use_skill"
    USE_ITEM = "use_item"
    FLEE = "flee"


@dataclass
class BattleAction:
    action_type: BattleActionType
    skill_name: Optional[str] = None
    item_id: Optional[str] = None


class Battle:
    def __init__(self, attacker: Combatant, defender: Combatant):
        if not attacker.is_alive or not defender.is_alive:
            raise ValueError("Both combatants must be alive to start a battle")
        self._attacker = attacker
        self._defender = defender
        self._current_turn_owner_id = attacker.id
        self._is_finished = False
        self._winner: Optional[Combatant] = None
        self._flee_attemps: Dict[str, int] = {attacker.id: 0, defender.id: 0}

    @property
    def is_finished(self) -> bool:
        return self._is_finished

    @property
    def winner(self) -> Optional[Combatant]:
        return self._winner

    def get_combatant_by_id(self, combatant_id: str) -> Combatant:
        if combatant_id == self._attacker.id:
            return self._attacker
        elif combatant_id == self._defender.id:
            return self._defender
        else:
            raise ValueError("Combatant not in this battle")

    def _end_battle(self, winner: Combatant) -> None:
        self._is_finished = True
        self._winner = winner

    def _calculate_base_damage(self, attacker: Combatant) -> int:
        # Урон = сила
        base = attacker.stats.strength
        return base

    def _is_critical_hit(self, attacker: Combatant, defender: Combatant) -> bool:
        # Шанс крита = (ловкость атакующего) / (ловкость защищающегося + 10)
        crit_chance = attacker.stats.agility / (defender.stats.agility + 10)

        # TODO: увеличить шанс крита
        return random() < min(crit_chance, 0)  # макс 50%

    def _can_flee(self, fleeing: Combatant, opponent: Combatant) -> bool:
        # шас побега растет с каждой попыткой
        attemps = self._flee_attemps[fleeing.id]
        base_chance = 0.3 + (attemps * 0.2)  # 30% 40% 70%
        agility_factor = fleeing.stats.agility / (opponent.stats.agility + 1)
        total_chance = min(base_chance * agility_factor, 0.9)
        success = random() < total_chance
        if success:
            return True
        else:
            self._flee_attemps[fleeing.id] += 1
            return False

    def perform_action(self, acting_combatant_id: str, action: BattleAction) -> dict:
        if self._is_finished:
            raise ValueError("Battle is already finished")

        if acting_combatant_id != self._current_turn_owner_id:
            raise ValueError("Not your turn")

        actor = self.get_combatant_by_id(acting_combatant_id)
        opponent = self._defender if actor.id == self._attacker.id else self._attacker

        result = {
            "action": action.action_type.value,
            "success": True,
            "details": ""
        }

        if action.action_type == BattleActionType.ATTACK:
            damage = self._calculate_base_damage(actor)
            if self._is_critical_hit(actor, opponent):
                damage = int(damage * 1.5)
                result["details"] = "Critical hit!"
            opponent._take_damage(damage)
            result["damage"] = damage

        elif action.action_type == BattleActionType.FLEE:
            if self._can_flee(actor, opponent):
                result["details"] = "Fled successfully!"
                self._end_battle(opponent)  # Победитель - тот, кто остался
                self._current_turn_owner_id = None
                return result
            else:
                result["details"] = "Failed to flee!"
                result["success"] = False

        elif action.action_type == BattleActionType.USE_SKILL:
            if not action.skill_name:
                raise ValueError("Skill name is required")
            try:
                effect = actor._use_skill(action.skill_name)
                skill = effect["skill"]
                value = effect['effect_value']

                if skill.skill_type == SkillType.DAMAGE:
                    opponent._take_damage(value)
                    result['damage'] = value
                    result["details"] = f'Used {skill.name} for {value} damage!'
                elif skill.skill_type == SkillType.HEAL:
                    actor._current_hp = min(
                        actor.stats.max_hp, actor._current_hp + value)
                    result["heal"] = value
                    result["details"] = f"Used {skill.name} and healed for {value} HP!"
                else:
                    result['details'] = f"Used {skill.name} (effect pending)"
            except ValueError as e:
                result["success"] = False
                result["details"] = str(e)

        # TODO: UseItem - добавить позже

        # Проверка смерти
        if not opponent.is_alive:
            self._end_battle(actor)

        # Передача хода
        if not self._is_finished:
            self._current_turn_owner_id = opponent.id

            # Уменьшаем colldown у того, кто НЕ ходил (т.е у opponent)
            opponent._reduce_colldowns()

        return result
