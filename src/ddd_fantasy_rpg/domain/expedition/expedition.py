from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from .expedition_event import ExpeditionEvent, PlayerDuelEncounter
from .expedition_distance import ExpeditionDistance
from .expedition_status import ExpeditionStatus
from ..common.time_provider import TimeProvider
from ..common.exceptions import ExpeditionNotActiveError




@dataclass
class Expedition:
    player_id: str
    distance: ExpeditionDistance
    start_time: datetime
    end_time: datetime
    status: ExpeditionStatus = ExpeditionStatus.ACTIVE
    outcome: Optional[ExpeditionEvent] = None

    def __post_init__(self):
        if self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")

    @classmethod
    def start_for(cls, player_id: str, distance: ExpeditionDistance, time_provider: TimeProvider) -> "Expedition":
        now = time_provider.now()
        end = now + timedelta(minutes=distance.duration_minutes)
        return cls(
            player_id=player_id,
            distance=distance,
            start_time=now,
            end_time=end,
            status=ExpeditionStatus.ACTIVE
        )

    def is_finished(self, time_provider: TimeProvider) -> bool:
        return time_provider.now() >= self.end_time

    def interrupt_for_duel(self, opponent_player_id: str) -> None:
        """Прерывает вылазку для дуэли"""
        if self.status != ExpeditionStatus.ACTIVE:
            raise ExpeditionNotActiveError()
        self.status = ExpeditionStatus.INTERRUPTED
        self.outcome = PlayerDuelEncounter(
            opponent_player_id=opponent_player_id)

    def complete_with_event(self, event: ExpeditionEvent) -> None:
        """Завершаем вылазку с событие (если не прервана)."""
        # if self.status == ExpeditionStatus.INTERRUPTED:
        #     raise ValueError("Expedition already interrupted")
        
        self.status = ExpeditionStatus.COMPLETED
        self.outcome = event

