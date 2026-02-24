from dataclasses import dataclass
from ..monster.monster import Monster
from ..monster.monster import Monster


class ExpeditionEvent:
    """Базовый класс для событий в вылазке."""
    pass


@dataclass
class MonsterEncounter(ExpeditionEvent):
    monster: Monster


@dataclass
class TraderEncounter(ExpeditionEvent):
    # TODO: На будущее
    pass


@dataclass
class ResourceGathering(ExpeditionEvent):
    resource_type: str
    amount: int


@dataclass
class PlayerDuelEncounter(ExpeditionEvent):
    opponent_player_id: str

