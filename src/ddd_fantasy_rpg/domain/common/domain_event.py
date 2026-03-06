import uuid
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass(kw_only=True)
class DomainEvent(ABC):
    
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    occurred_on: datetime = field(default_factory=lambda: datetime.now(timezone.utc))