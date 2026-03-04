from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional
from collections import deque

from ddd_fantasy_rpg.domain.common.domain_event import DomainEvent

from ddd_fantasy_rpg.domain.battle.events import BattleStarted, BattleFinished

from ddd_fantasy_rpg.domain.battle.combatant import Combatant

from ddd_fantasy_rpg.domain.battle.battle_result import BattleResult, BattleParticipant, PvpVictory, PlayerVictory, MonsterVictory
from ddd_fantasy_rpg.domain.battle.battle_action import BattleAction, BattleActionType
from ddd_fantasy_rpg.domain.battle.battle_action_result import BattleActionResult, AttackResult, FleeResult, ItemUseResult, SkillUseResult

from ddd_fantasy_rpg.domain.battle.battle_mechanics_service import BattleMechanicsService
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
    mechanics_service: BattleMechanicsService
    max_rounds: int = 100

    _turn_owner: BattleTurn = BattleTurn.ATTACKER
    _round_count: int = 0
    _winner: Optional[Combatant] = None
    _flee_attempts: Dict[str, int] = None
    _is_finished: bool = False

    def __post_init__(self):
        self._flee_attempts = {self.attacker.id: 0, self.defender.id: 0}

        self._pending_events: deque[DomainEvent] = deque()
        start_event = BattleStarted(
            battle_id=self.battle_id, attacker_id=self.attacker.id, defender_id=self.defender.id)
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

        result: BattleActionResult

        if action.action_type == BattleActionType.ATTACK:
            result = self._perform_attack(actor, opponent)

        elif action.action_type == BattleActionType.USE_SKILL:
            if not action.skill_id:
                raise DomainError(
                    "Для использования навыка требуется идентификатор навыка")
            result = self._perform_skill_use(actor, opponent, action.skill_id)

        elif action.action_type == BattleActionType.USE_ITEM:
            # TODO: Реализовать логику использвания предметов здесь в рамках битвы.
            result = ItemUseResult(
                action_type=BattleActionType.USE_ITEM,
                item_name=action.item_name or "unknow",
                success=True
            )
        elif action.action_type == BattleActionType.FLEE:
            result = self._perform_flee(actor, opponent)

        else:
            raise DomainError(
                f"Неизвестный тип действия: {action.action_type}")

        if not self._is_finished and self._round_count >= self.max_rounds:
            # Тайм-аут: Определить победителя по HP или объявить ничью
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
        damage, is_critical = self.mechanics_service.calculate_damage_and_crit(
            actor, opponent)
        opponent.take_damage(damage)

        if not opponent.is_alive:
            self._end_battle(actor)

        return AttackResult(
            action_type=BattleActionType.ATTACK,
            success=True,
            damage=damage,
            is_critical=is_critical,
        )

    def _perform_skill_use(self, actor: Combatant, opponent: Combatant, skill_id: str) -> SkillUseResult:

        skill = next(
            (s for s in actor.available_skills if s.name == skill_id), None)
        if not skill:
            raise DomainError(
                f"Навык '{skill_id}' недоступен для бойца '{actor.id}'.")

        skill_type, effect_value, details = self.mechanics_service.calculate_skill_effect(
            skill, actor, opponent)

        if skill_type == SkillType.DAMAGE:
            opponent.take_damage(effect_value)
            if not opponent.is_alive:
                self._end_battle(actor)
            return SkillUseResult(
                action_type=BattleActionType.USE_SKILL,
                success=True,
                skill_name=skill.name,
                damage=effect_value,
            )
        elif skill_type == SkillType.HEAL:
            actor.take_heal(effect_value)
            return SkillUseResult(
                action_type=BattleActionType.USE_SKILL,
                success=True,
                skill_name=skill.name,
                heal=effect_value,
            )

        actor.use_skill(skill.name)
        return SkillUseResult(
            action_type=BattleActionType.USE_SKILL,
            success=False,
            skill_name=skill.name,
        )

    def _perform_flee(self, actor: Combatant, opponent: Combatant) -> FleeResult:
        attemts = self._flee_attempts[actor.id]
        can_flee = self.mechanics_service.calculate_flee_success(
            actor, opponent, attemts)

        if can_flee:
            self._end_battle(None)
            return FleeResult(
                action_type=BattleActionType.FLEE,
                success=True,
            )
        else:
            self._flee_attempts[actor.id] += 1
            return FleeResult(
                action_type=BattleActionType.FLEE,
                success=False,
            )

    def _advance_turn(self) -> None:
        self._turn_owner = BattleTurn.DEFENDER if self._turn_owner == BattleTurn.ATTACKER else BattleTurn.ATTACKER
        self._round_counter += 1

        self.attacker.reduce_colldowns()
        self.defender.reduce_colldowns()

    def _end_battle(self, winner: Optional[Combatant]) -> None:
        self._winner = winner
        self._is_finished = True
        
        if winner:
            result = self.get_battle_result()
            loser = self.get_opponent(winner.id)
            finish_event = BattleFinished(
                battle_id=self.battle_id,
                result=result,
                winner_id=winner.id,
                loser_id=loser.id,
            )
            self._pending_events.append(finish_event)
            
    def pop_pending_events(self) -> list[DomainEvent]:
        events = list(self._pending_events)
        self._pending_events.clear()
        return events

    def get_battle_result(self) -> Optional[BattleResult]:
        if not self.is_finished:
            return None

        winner = self.winner
        if not self.winner:
            return BattleResult(outcome=None, is_pvp=False)

        loser = self.get_opponent(self.winner.id)

        winner_participant = BattleParticipant(
            id=self.winner.id, is_player=self.winner.is_player, is_monster=self.winner.is_monster)
        loser_participant = BattleParticipant(
            id=loser.id, is_player=loser.is_player, is_monster=loser.is_monster)

        is_pvp = self.winner.is_player and loser.is_player

        if winner.is_player and loser.is_player:
            loot = []
            exp_gained = 50
            outcome = PlayerVictory(
                winner=winner_participant, loser=loser_participant, loot=loot, experience_gained=exp_gained)
        elif winner.is_monster and loser.is_player:
            loot = []
            outcome = MonsterVictory(
                winner=winner_participant, loser=loser_participant)
        elif is_pvp:
            loot = []
            outcome = PvpVictory(winner=winner_participant,
                                 loser=loser_participant, loot=loot)
        else:
            raise RuntimeError("Неожиданный сценарий развития событий в бою.")

        return BattleResult(outcome=outcome, is_pvp=is_pvp)

    @classmethod
    def start(cls, battle_id: str, attacker: Combatant, defender: Combatant, mechanics_service: BattleMechanicsService) -> "Battle":
        return cls(
            battle_id=battle_id,
            attacker=attacker,
            defender=defender,
            mechanics_service=mechanics_service
        )
