from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional, Union

from .moster import Monster


class ExpeditionDistance(Enum):
    NEAR = ("near", 1) # 10
    MEDIUM = ("medium", 1) # 20
    FAR = ("far", 1) # 30

    def __init__(self, key: str, duration: int):
        self.key = key
        self.duration_minutes = duration


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
    opponent_telegram_id: int


@dataclass
class Expedition:
    player_id: str
    distance: ExpeditionDistance
    start_time: datetime
    end_time: datetime
    outcome: Optional[ExpeditionEvent] = None

    def __post_init__(self):
        if self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")

    @classmethod
    def start_for(cls, player_id: str, distance: ExpeditionDistance) -> "Expedition":
        now = datetime.now(timezone.utc)
        end = now + timedelta(minutes=distance.duration_minutes)
        return cls(
            player_id=player_id,
            distance=distance,
            start_time=now,
            end_time=end
        )

    def is_finished(self) -> bool:
        return datetime.now(timezone.utc) >= self.end_time
    
    def complete_with(self, event: ExpeditionEvent) -> None:
        if not self.is_finished():
            raise ValueError("Cannot complete unfinished expedition")
        
        self.outcome = event