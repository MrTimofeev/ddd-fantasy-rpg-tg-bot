from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional
from collections import deque

from ddd_fantasy_rpg.domain.common.domain_event import DomainEvent

from ddd_fantasy_rpg.domain.battle.events import BattleStarted, BattleFinished

from ddd_fantasy_rpg.domain.battle.combatant import Combatant

from ddd_fantasy_rpg.domain.battle.battle_result import BattleResult, BattleParticipant, PvpVictory, PlayerVictory, MonsterVictory
from ddd_fantasy_rpg.domain.battle.battle_action import BattleAction, BattleActionType
from ddd_fantasy_rpg.domain.battle.battle_action_result import BattleActionResult, AttackResult, FleeResult, ItemUseResult, SkillUseResult

from ddd_fantasy_rpg.domain.common.random_provider import RandomProvider
from ddd_fantasy_rpg.domain.common.base_exceptions import DomainError

from ddd_fantasy_rpg.domain.skills.skill_type import SkillType


class BattleTurn(Enum):
    ATTACKER = "attacker"
    DEFENDER = "defender"


@dataclass
class Battle:
    battle_id: str
    attacker: Combatant
    defender: Combatant
    random_provider: RandomProvider
    max_rounds: int = 100

    _turn_owner: BattleTurn = BattleTurn.ATTACKER
    _round_count: int = 0
    _winner: Optional[Combatant] = None

    _flee_attempts: Dict[str, int] = field(default_factory=dict)
    _is_finished: bool = False

    def __post_init__(self):
        self._flee_attempts[self.attacker.id] = 0
        self._flee_attempts[self.attacker.id] = 0

        self._pending_events: deque[DomainEvent] = deque()
        start_event = BattleStarted(
            battle_id=self.battle_id, attacker_id=self.attacker.id,
            defender_id=self.defender.id
        )
        self._pending_events.append(start_event)

    @property
    def id(self) -> str:
        return self.battle_id

    @property
    def is_finished(self) -> bool:
        return self._is_finished

    @property
    def winner(self) -> Optional[Combatant]:
        return self._winner

    def get_opponent(self, combatant_id: str) -> Combatant:
        if combatant_id == self.attacker.id:
            return self.defender
        elif combatant_id == self.defender.id:
            return self.attacker
        else:
            raise DomainError(
                f"Участник с ID {combatant_id} не участвует в этом сражении.")

    def get_combatant_by_id(self, combatant_id: str) -> Combatant:
        if combatant_id == self.attacker.id:
            return self.attacker
        elif combatant_id == self.defender.id:
            return self.defender
        else:
            raise DomainError(
                f"Участник с ID {combatant_id} не участвует в этом сражении.")

    def perform_action(self, acting_combatant_id: str, action: BattleAction) -> BattleActionResult:
        if self.is_finished:
            raise DomainError("Действие невозможно: битва уже закончилась")

        actor = self.get_combatant_by_id(acting_combatant_id)
        opponent = self.get_opponent(acting_combatant_id)

        if not actor.is_alive:
            raise DomainError(f"Боец {actor.id} мертв и не может действовать.")

        result: BattleActionResult

        if action.action_type == BattleActionType.ATTACK:
            result = self._perform_attack(actor, opponent)
        elif action.action_type == BattleActionType.USE_SKILL:
            if not action.skill_id:
                raise ValueError(
                    "Для использования необходимо указать идентификатор навыка.")
            result = self._perform_skill_use(actor, opponent, action.skill_id)
        elif action.action_type == BattleActionType.USE_ITEM:
            # TODO: Реализовать логику использвания предметов здесь в рамках битвы
            result = ItemUseResult(
                action_type=action.action_type,
                success=False,
                item_name=action.item_name or "Unknow",
                details="Логика использования предмета пока не реализована."
            )
        elif action.action_type == BattleActionType.FLEE:
            result = self._perform_flee(actor, opponent)
        else:
            raise ValueError(
                f"Неподдерживаемый тип действия: {action.action_type}")

        if self.attacker.current_hp <= 0:
            self._end_battle(self.defender)
        elif self.defender.current_hp <= 0:
            self._end_battle(self.attacker)
        elif self._round_count >= self.max_rounds:
            if self.attacker.current_hp > self.defender.current_hp:
                self._end_battle(self.attacker)
            elif self.defender.current_hp > self.attacker.current_hp:
                self._end_battle(self.defender)
            else:
                self._end_battle(None)  # Ничья

        if not self._is_finished:
            self._advance_turn()

        return result

    def _perform_attack(self, actor: Combatant, opponent: Combatant) -> AttackResult:
        damage, is_critical = self._calculate_damage_and_crit(actor, opponent)
        opponent.take_damage(damage)

        details = f"{actor.name} attacks {opponent.name} for {damage} damage." + \
            (" Critical hit!" if is_critical else "")

        return AttackResult(
            action_type=BattleActionType.ATTACK,
            success=True,
            damage=damage,
            is_critical=is_critical,
            details=details
        )

    def _perform_skill_use(self, actor: Combatant, opponent: Combatant, skill_id: str) -> SkillUseResult:

        try:
            skill_effect = actor.use_skill(skill_id)
        except Exception as e:
            return SkillUseResult(
                action_type=BattleActionType.USE_SKILL,
                success=False,
                skill_name=skill_id,
                details=str(e)
            )

        if skill_effect.skill_type.name == SkillType.DAMAGE:
            opponent.take_damage(skill_effect.effect_value)
            return SkillUseResult(
                action_type=BattleActionType.USE_SKILL,
                success=True,
                skill_name=skill_effect.skill_name,
                damage=skill_effect.effect_value,
                details=f"{actor.name} uses {skill_effect.skill_name} on {opponent.name} for {skill_effect.effect_value} damage."
            )
        elif skill_effect.skill_type.name == SkillType.HEAL:
            actor.take_heal(skill_effect.effect_value)
            return SkillUseResult(
                action_type=BattleActionType.USE_SKILL,
                success=True,
                skill_name=skill_effect.skill_name,
                heal=skill_effect.effect_value,
                details=f"{actor.name} uses {skill_effect.skill_name} and heals for {skill_effect.effect_value}."
            )
        else:
            return SkillUseResult(
                action_type=BattleActionType.USE_SKILL,
                success=True,
                skill_name=skill_effect.skill_name,
                details=f"{actor.name} uses {skill_effect.skill_name} ({skill_effect.skill_type.name})."
            )

    def _perform_flee(self, actor: Combatant, opponent: Combatant) -> FleeResult:
        attemts = self._flee_attempts[actor.id]
        can_flee = self._can_flee(actor, opponent, attemts)

        if can_flee:
            self._end_battle(opponent)
            return FleeResult(
                action_type=BattleActionType.FLEE,
                success=True,
                details=f"{actor.name} successfully flees from the battle!"
            )
        else:
            self._flee_attempts[actor.id] += 1
            return FleeResult(
                action_type=BattleActionType.FLEE,
                success=False,
                details=f"{actor.name} tries to flee but fails!"
            )

    def _advance_turn(self) -> None:
        self._turn_owner = BattleTurn.DEFENDER if self._turn_owner == BattleTurn.ATTACKER else BattleTurn.ATTACKER
        self._round_counter += 1

        self.attacker.reduce_colldowns()
        self.defender.reduce_colldowns()

    def _calculate_base_damage(self, attacker: Combatant) -> int:
        """Расчитывает базовый урон аттакующего"""
        return attacker.stats.damage

    def _is_critical_hit(self, attacker: Combatant, defender: Combatant) -> bool:
        """Определяет, блы ли критический удар."""
        crit_chance = attacker.stats.agility / (defender.stats.agility + 10)
        roll = self.random_provider.random()
        return roll < crit_chance

    def _calculate_damage_and_crit(self, attacker: Combatant, defender: Combatant) -> tuple[int, bool]:
        """Рассчитывает урон и проверят кртитический удар."""
        base_damage = self._calculate_base_damage(attacker)
        is_critical = self._is_critical_hit(attacker, defender)
        damage = base_damage if not is_critical else int(base_damage * 1.5)
        effective_damage = max(1, damage - defender.stats.armor)
        return effective_damage, is_critical

    def _can_flee(self, fleeing: Combatant, opponent: Combatant, flee_attempts: int) -> bool:
        base_chance = 0.3 - (flee_attempts * 0.2)
        agility_factor = fleeing.stats.agility / (opponent.stats.agility + 1)
        total_chance = min(max(base_chance * agility_factor, 0.05), 0.9)
        roll = self.random_provider.random()
        return roll < total_chance

    def _end_battle(self, winner: Optional[Combatant]) -> None:
        self._winner = winner
        self._is_finished = True

        result = self.get_battle_result()
        if result and self._winner:
            loser = self.get_opponent(self._winner.id)
            finish_event = BattleFinished(
                battle_id=self.battle_id,
                result=result,
                winner_id=self._winner.id,
                loser_id=loser.id,
            )
            self._pending_events.append(finish_event)

    def pop_pending_events(self) -> list[DomainEvent]:
        events = list(self._pending_events)
        self._pending_events.clear()
        return events

    def get_battle_result(self) -> Optional[BattleResult]:
        if not self._winner:
            return None

        winner = self._winner
        loser = self.get_opponent(winner.id)

        winner_participant = BattleParticipant(
            id=winner.id,
            name=winner.name,
            is_player=winner.is_player,
            is_monster=winner.is_monster,
            final_hp=winner.current_hp
        )
        loser_participant = BattleParticipant(
            id=loser.id,
            name=loser.name,
            is_player=loser.is_player,
            is_monster=loser.is_monster,
            final_hp=loser.current_hp,
        )

        is_pvp = winner.is_player and loser.is_player
        loot = [] # Лут определяется вне агрегата Battle 
        exp_gained = 50 if winner.is_player else 0 # тестовые значение 

        if winner.is_player and loser.is_player:
            outcome = PlayerVictory(
                winner=winner_participant,
                loser=loser_participant,
                loot=loot,
                experience_gained=exp_gained    
            )
        elif winner.is_monster and loser.is_player:
            outcome = MonsterVictory(
                winner=winner_participant,
                loser=loser_participant
            )
        elif is_pvp:
            outcome = PvpVictory(
                winner=winner_participant,
                loser=loser_participant,
                loot=loot, # TODO: сделать передачу предметов проигравшего победителю
            )

        else:
            raise RuntimeError("Неожиданный сценарий развития событий в бою.")

        return BattleResult(outcome=outcome, is_pvp=is_pvp)

    @classmethod
    def start(cls, battle_id: str, attacker: Combatant, defender: Combatant, random_provider: RandomProvider) -> "Battle":
        return cls(
            battle_id=battle_id,
            attacker=attacker,
            defender=defender,
            random_provider=random_provider
        )
