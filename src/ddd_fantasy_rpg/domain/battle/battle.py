from typing import Dict, Optional

from ddd_fantasy_rpg.domain.battle.combatant import Combatant, CombatantType

from ddd_fantasy_rpg.domain.battle.exeptions import (
    CombatantNotAliveError,
    CombatantNotInBattleError,
    NotYourTurnError,
    BattleAlreadyFinishedError,
)

from ddd_fantasy_rpg.domain.battle.battle_result import BattleResult, BattleParticipant, PvpVictory, PlayerVictory, MonsterVictory
from ddd_fantasy_rpg.domain.battle.battle_action import BattleAction, BattleActionType
from ddd_fantasy_rpg.domain.battle.battle_action_result import BattleActionResult

from ddd_fantasy_rpg.domain.battle.battle_mechanics_service import BattleMechanicsService


class Battle:
    def __init__(self, battle_id: str, attacker: Combatant, defender: Combatant):
        if not attacker.is_alive or not defender.is_alive:
            raise CombatantNotAliveError()
        self._id = battle_id
        self._attacker = attacker
        self._defender = defender
        self._current_turn_owner_id = attacker.id
        self._is_finished = False
        self._winner: Optional[Combatant] = None
        self._flee_attempts: Dict[str, int] = {attacker.id: 0, defender.id: 0}

    @property
    def id(self) -> str:
        return self._id

    @property
    def is_finished(self) -> bool:
        return self._is_finished

    @property
    def winner(self) -> Optional[Combatant]:
        return self._winner

    def _end_battle(self, winner: Combatant) -> None:
        self._is_finished = True
        self._winner = winner

    def _advance_turn(self, next_combatant: Combatant) -> None:
        """Передаем ход следующему игроку и уменьшает кулдауны."""
        if not self.is_finished:
            self._current_turn_owner_id = next_combatant.id
            next_combatant.reduce_colldowns()

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
        battle_mechanics: BattleMechanicsService
    ) -> BattleActionResult:
        if self._is_finished:
            raise BattleAlreadyFinishedError()

        if acting_combatant_id != self._current_turn_owner_id:
            raise NotYourTurnError()

        actor = self.get_combatant_by_id(acting_combatant_id)
        opponent = self._defender if actor.id == self._attacker.id else self._attacker

        if action.action_type == BattleActionType.ATTACK:
            result = battle_mechanics.perform_attack(
                actor, opponent, self._flee_attempts)
            opponent.take_damage(result.damage)
            if not opponent.is_alive:
                self._end_battle(actor)
                
            self._advance_turn(opponent)
            return result

        elif action.action_type == BattleActionType.FLEE:
            result = battle_mechanics.perform_flee(
                actor, opponent, self._flee_attempts)
            if result.success:
                self._end_battle(opponent)
                self._current_turn_owner_id = None
            else:
                self._flee_attempts[actor.id] = self._flee_attempts.get(
                    actor.id, 0) + 1
                self._advance_turn(opponent)
            return result

        elif action.action_type == BattleActionType.USE_SKILL:
            if not action.skill_name:
                raise ValueError("Skill name is required")

            result = battle_mechanics.perform_skill_use(
                actor, action.skill_name)
            if result.success and result.damage:
                opponent.take_damage(result.damage)
            elif result.success and result.heal:
                opponent.take_heal(result.heal)
            self._advance_turn(opponent)
            return result

        elif action.action_type == BattleActionType.USE_ITEM:
            if not action.item_name:
                raise ValueError("Item ID is required")
            result = battle_mechanics.perform_item_use(action.item_name)
            # TODO: Применить эффект предмета
            self._advance_turn(opponent)
            return result

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

    @classmethod
    def start(cls, battle_id: str, attacker: Combatant, defender: Combatant) -> "Battle":
        if not attacker.is_alive or not defender.is_alive:
            raise CombatantNotAliveError()
        return cls(battle_id, attacker, defender)
