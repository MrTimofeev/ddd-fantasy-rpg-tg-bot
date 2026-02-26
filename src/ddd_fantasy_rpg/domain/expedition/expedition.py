from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from ddd_fantasy_rpg.domain.expedition.expedition_event import ExpeditionEvent, PlayerDuelEncounter, MonsterEncounter, TraderEncounter, ResourceGathering
from ddd_fantasy_rpg.domain.expedition.expedition_distance import ExpeditionDistance
from ddd_fantasy_rpg.domain.expedition.expedition_status import ExpeditionStatus
from ddd_fantasy_rpg.domain.common.time_provider import TimeProvider
from ddd_fantasy_rpg.domain.expedition.exeptions import ExpeditionNotActiveError




@dataclass
class Expedition:
    player_id: str
    distance: ExpeditionDistance
    start_time: datetime
    end_time: datetime
    status: ExpeditionStatus = ExpeditionStatus.NO_ACTIVE
    outcome: Optional[ExpeditionEvent] = None

    def __post_init__(self):
        if self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")

    @classmethod
    def start_for(
        cls,
        player_id: str,
        distance: ExpeditionDistance,
        event: ExpeditionEvent,
        time_provider: TimeProvider
    ) -> "Expedition":
        now = time_provider.now()
        end = now + timedelta(minutes=distance.duration_minutes)
        return cls(
            player_id=player_id,
            distance=distance,
            start_time=now,
            end_time=end,
            status=ExpeditionStatus.ACTIVE,
            outcome=event
        )

    def is_finished(self, time_provider: TimeProvider) -> bool:
        return time_provider.now() >= self.end_time

    def interrupt_for_duel(self, opponent_player_id: str) -> None:
        """Прерывает вылазку для дуэли"""
        if self.status != ExpeditionStatus.ACTIVE:
            raise ExpeditionNotActiveError()
        self.outcome = PlayerDuelEncounter(
            opponent_player_id=opponent_player_id)

    def complete(self) -> None:
        """Завершаем вылазку"""
        self.status = ExpeditionStatus.COMPLETED
        
    
    def start_event(self, event) -> None:
        """Начинает событие, устанавливает статуст в зависимости от события"""
        if isinstance(event, MonsterEncounter):
            self.status = ExpeditionStatus.PVE
        elif isinstance(event, PlayerDuelEncounter):
            self.status = ExpeditionStatus.PVP
        elif isinstance(event, TraderEncounter):
            self.status = ExpeditionStatus.TRADER
        elif isinstance(event, ResourceGathering):
            self.status = ExpeditionStatus.RESOURCE
        else:
            raise ValueError("Неизвестное событие")
    
    def complete_event(self) -> None:
        """Завершает событие"""
        self.status = ExpeditionStatus.NO_ACTIVE

