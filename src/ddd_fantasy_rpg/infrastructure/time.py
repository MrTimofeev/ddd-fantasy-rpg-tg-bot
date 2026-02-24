from datetime import datetime, timezone

from ddd_fantasy_rpg.domain.common.time_provider import TimeProvider


class UtcTimeProvider(TimeProvider):
    def now(self) -> datetime:
        return datetime.now(timezone.utc)