from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from ddd_fantasy_rpg.domain.expedition.expedition_event import ExpeditionEvent, PlayerDuelEncounter, MonsterEncounter, TraderEncounter, ResourceGathering
from ddd_fantasy_rpg.domain.expedition.expedition_distance import ExpeditionDistance
from ddd_fantasy_rpg.domain.expedition.expedition_status import ExpeditionStatus
from ddd_fantasy_rpg.domain.common.base_exceptions import DomainError
from ddd_fantasy_rpg.domain.common.domain_event import DomainEvent
from ddd_fantasy_rpg.domain.expedition.events import ExpeditionStarted, ExpeditionCompleted


@dataclass
class Expedition:
    id: str
    player_id: str
    distance: ExpeditionDistance
    start_time: datetime
    planned_end_time: datetime
    status: ExpeditionStatus = ExpeditionStatus.ACTIVE
    outcome: Optional[ExpeditionEvent] = None
    _travel_completed_at: Optional[datetime] = None

    def __post_init__(self):
        if self.status == ExpeditionStatus.ACTIVE and self.outcome is None:
            raise DomainError(
                f"Активная экспедиция {self.id} должна иметь запланированный результат.")
            
        self._pending_events: deque[DomainEvent] = deque()
        start_events = ExpeditionStarted(expedition_id=self.id, player_id=self.player_id)
        self._pending_events.append(start_events)
        

    @property
    def is_active(self) -> bool:
        return self.status == ExpeditionStatus.ACTIVE

    @property
    def is_travel_completed(self) -> bool:
        return self._travel_completed_at is not None

    @property
    def is_completed(self) -> bool:
        return self.status == ExpeditionStatus.COMPLETED

    @property
    def is_pvp(self) -> bool:
        return self.outcome is not None and isinstance(self.outcome, PlayerDuelEncounter)

    def is_finished(self, current_time: datetime) -> bool:
        if self._travel_completed_at is not None:
            return True

        if current_time >= self.planned_end_time:
            self._travel_completed_at = current_time
            return True

        return False

    def complete_travel(self, outcome: ExpeditionEvent) -> None:
        if self.status != ExpeditionStatus.ACTIVE:
            raise DomainError(
                f"Невозможно завершить путешествие для экспедиции {self.id}. Она неактивна (статус: {self.status.value}).")
        if self._travel_completed_at is None:
            raise DomainError(
                f"Согласно `is_finished`, поездка для экспедиции {self.id} еще не завершена.")
        pass

    def confirm_event_processed(self) -> None:
        if not self.is_travel_completed:
            raise DomainError(
                f"Невозможно подтвердить обработку события для экспедиции {self.id}. Путешествие еще не завершено.")

        self.status = ExpeditionStatus.COMPLETED
        
        completion_event = ExpeditionCompleted(expedition_id=self.id, player_id=self.player_id, outcome=self.outcome)
        
    def pop_pending_events(self) -> list[DomainEvent]:
        events = list(self._pending_events)
        self._pending_events.clear()
        return events

    def __repr__(self) -> str:
        return f"<Expedition id={self.id} player_id={self.player_id} status={self.status.value} planned_end={self.planned_end_time}>"
