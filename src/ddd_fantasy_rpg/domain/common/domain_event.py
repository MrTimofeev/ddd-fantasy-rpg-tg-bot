import uuid
from abc import ABC
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass
class DomainEvent(ABC):
    
    event_id: str = None
    occurred_on: datetime = None
    
    def __post_init__(self):
        if self.event_id is None:
            self.event_id = str(uuid.uuid4())
        if self.occurred_on is None:
            self.occurred_on = datetime.now(timezone.utc)
        