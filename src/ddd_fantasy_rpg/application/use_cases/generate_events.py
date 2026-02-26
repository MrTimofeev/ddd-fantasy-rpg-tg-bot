from ddd_fantasy_rpg.domain.common import RandomProvider
from ddd_fantasy_rpg.domain.expedition.expedition_event_generator import generate_monster_for_distance
from ddd_fantasy_rpg.domain.expedition.expedition_event import MonsterEncounter, ExpeditionEvent, PlayerDuelEncounter
from ddd_fantasy_rpg.domain.expedition.expedition_distance import ExpeditionDistance


class GenerateEventUseCase:
    """
    Use Case для генерации события
    """

    def __init__(
        self,
        random_provider: RandomProvider
    ):
        self._randome_provider = random_provider

    async def execute(
        self,
        distance: ExpeditionDistance,
    ) -> ExpeditionEvent:
        """
        Случано генерирует событие для игрока
        """
        if self._randome_provider.random() < 0.1:
            return PlayerDuelEncounter(None)

        monster = generate_monster_for_distance(
            distance, self._randome_provider)
        return MonsterEncounter(monster)
