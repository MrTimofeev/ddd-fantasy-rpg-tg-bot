from dataclasses import dataclass
from typing import Optional

from .battle_action import BattleActionType


@dataclass(frozen=True)
class BattleActionResult:
    pass


@dataclass(frozen=True)
class AttackResult(BattleActionResult):
    action_type: BattleActionType
    success: bool
    damage: int
    is_critical: bool = False
    details: str = ""


@dataclass(frozen=True)
class SkillUseResult(BattleActionResult):
    action_type: BattleActionType
    success: bool
    skill_name: str
    damage: Optional[int] = None
    heal: Optional[int] = None
    details: str = ""


@dataclass(frozen=True)
class FleeResult(BattleActionResult):
    action_type: BattleActionType
    success: bool
    details: str = ""


@dataclass(frozen=True)
class ItemUseResult(BattleActionResult):
    action_type: BattleActionType
    success: bool
    item_name: str
    daetails: str = ""

