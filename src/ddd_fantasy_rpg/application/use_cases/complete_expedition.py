from ddd_fantasy_rpg.domain.expedition import Expedition, ExpeditionEvent, MonsterEncounter
from ddd_fantasy_rpg.domain.repositories.expedition_repository import ExpeditionRepository
from ddd_fantasy_rpg.domain.repositories.player_repository import PlayerRepository
from ddd_fantasy_rpg.domain.expedition_event_generator import generate_event_for_expedition
from ddd_fantasy_rpg.application.use_cases.start_battle import StartBattleUseCase


class CompleteExpeditionUseCase:
    def __init__(
        self,
        expedition_repository: ExpeditionRepository,
        player_repository: PlayerRepository,
        start_battle_use_case: StartBattleUseCase,
    ):
        self._expedition_repo = expedition_repository
        self._player_repo = player_repository
        self._start_battle_uc = start_battle_use_case
        
    async def execute(self, player_id: str) -> ExpeditionEvent:
        # 1. Получаем активную вылазку
        expedition = await self._expedition_repo.get_by_player_id(player_id)
        if not expedition:
            raise ValueError("No active expedition found")
        if not expedition.is_finished():
            raise ValueError("Expedition is not finished yet")

        # 2. Генерируем событие
        event = generate_event_for_expedition(expedition.distance)
        
        # 3. Если монстр - запускаем бой
        if isinstance(event, MonsterEncounter):
            # Бой запускается, но результат события - все равно MonsterEncounter
            # (фактически исход боя будет позже)
            
            try:
                await self._start_battle_uc.execute(player_id, event.monster)
            except Exception as e:
                print(f"Ошибка Боя: {e}")

        # 4. Сохраняем результат вылазки
        expedition.complete_with(event)
    
        await self._expedition_repo.save(expedition)
        
        return event
        
        