from typing import Union

from ddd_fantasy_rpg.domain import Player, Monster
from ddd_fantasy_rpg.domain.repositories.player_repository import PlayerRepository
from ddd_fantasy_rpg.domain.repositories.battle_repository import BattleRepository
from ddd_fantasy_rpg.domain.combatant_factory import (
    create_combatant_from_player,
    create_combatant_from_monster,
)
from ddd_fantasy_rpg.domain.battle import Battle


class StartBattleUseCase:
    """
    Use Case для старта битвы
    """
    def __init__(
        self,
        player_repository: PlayerRepository,
        battle_repository: BattleRepository,
    ):
        self._player_repo = player_repository
        self._battle_repo = battle_repository
        
    async def execute(
        self,
        player_id: str,
        opponent: Union[Monster, str] # str = opponent_player_id (для PVP)
    ) -> Battle:
        # 1. Загружаем игрока
        player = await self._player_repo.get_by_id(player_id)
        if not player:
            raise ValueError(f"Player {player_id} not found")
        
        # 2. Проверяем, нет ли активного боя
        active_battle = await self._battle_repo.get_active_battle_for_player(player_id)
        if active_battle:
            raise ValueError("Player is already in battle")
        
        # 3. Создаем Combatan'ов
        player_combatant = create_combatant_from_player(player)
        
        if isinstance(opponent, Monster):
            opponent_combatant = create_combatant_from_monster(opponent)
        else:
            opponent_player = await self._player_repo.get_by_id(opponent)
            if not opponent_player:
                raise ValueError("Opponent player not found")
            opponent_combatant = create_combatant_from_player(opponent_player)
        
        # 4. Создаем бой
        battle = Battle(player_combatant, opponent_combatant)
        
        # 5. Сохряняем
        await self._battle_repo.save(battle)
        
        return battle
        