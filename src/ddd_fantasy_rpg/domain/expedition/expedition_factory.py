from datetime import datetime, timedelta
import uuid

from ddd_fantasy_rpg.domain.expedition.expedition import Expedition
from ddd_fantasy_rpg.domain.expedition.expedition_distance import ExpeditionDistance
from ddd_fantasy_rpg.domain.expedition.expedition_status import ExpeditionStatus
from ddd_fantasy_rpg.domain.expedition.expedition_event_generator import ExpeditionEventGenerator
from ddd_fantasy_rpg.domain.common.time_provider import TimeProvider

class ExpeditionFactory:
    def __init__(
        self,
        event_generator: ExpeditionEventGenerator,
        time_provider: TimeProvider,
    ):
        self._generator = event_generator
        self._time_provider = time_provider
        
    
    def create_new_expedition(self, player_id: str, distance: ExpeditionDistance) -> Expedition:
        start_time = self._time_provider.now()
        planned_end_time =  start_time + timedelta(minutes=distance.duration_minutes)
        
        planned_outcome = self._generator.generate_event(distance)
        
        return Expedition(
            id=str(uuid.uuid4()),
            player_id=player_id,
            distance=distance,
            start_time=start_time,
            planned_end_time=planned_end_time,
            status=ExpeditionStatus.ACTIVE,
            outcome=planned_outcome
        )
