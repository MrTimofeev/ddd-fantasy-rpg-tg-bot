from dataclasses import dataclass
from enum import Enum
from typing import Optional


class BattleActionType(Enum):
    ATTACK = "attack"
    USE_SKILL = "use_skill"
    USE_ITEM = "use_item"
    FLEE = "flee"


@dataclass
class BattleAction:
    action_type: BattleActionType
    skill_name: Optional[str] = None
    item_name: Optional[str] = None

