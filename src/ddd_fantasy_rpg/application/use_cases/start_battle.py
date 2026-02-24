from ddd_fantasy_rpg.domain.common.unit_of_work import UnitOfWork
from ddd_fantasy_rpg.domain import Monster, Battle, Player, Combatant
from ddd_fantasy_rpg.domain.battle.combatant_factory import (
    create_combatant_from_player,
    create_combatant_from_monster,
)

from ddd_fantasy_rpg.domain.common.exceptions import PlayerNotFoundError, PlayerAlreadyInBattleError, SelfDuelError



class StartBattleUseCase:
    """
    Use Case для старта битвы
    """

    async def start_pve_battle(
        self,
        player_id: str,
        monster: Monster,
        uow: UnitOfWork,
    ) -> Battle:
        """Запускает PvE бой (игрок против монстра)."""
        player = await self._load_player(player_id, uow)
        opponent_combatant = create_combatant_from_monster(monster)
        return await self._create_battle(player, opponent_combatant, uow)

    async def start_pvp_battle(
        self,
        player1_id: str,
        player2_id: str,
        uow: UnitOfWork
    ) -> Battle:
        """Запускает PvP дуэль (игрок против игрока)."""
        player1 = await self._load_player(player1_id, uow)
        player2 = await self._load_player(player2_id, uow)
        
        if player1_id == player2_id:
            raise SelfDuelError()
        
        opponent_combatant = create_combatant_from_player(player2)
        return await self._create_battle(player1, opponent_combatant, uow)
        
        
    async def _load_player(
        self,
        player_id: str,
        uow: UnitOfWork,
    ) -> Player:
        """Загружает игрока и проверяет условия для боя."""
        player = await uow.players.get_by_id(player_id)
        if not player:
            raise PlayerNotFoundError(player_id)
        
        active_battle = await uow.battles.get_active_battle_for_player(player_id)
        if active_battle:
            raise PlayerAlreadyInBattleError(player_id)
        
        return player
    
    async def _create_battle(
        self,
        player: Player,
        opponent_combatant: "Combatant",
        uow: UnitOfWork,
    ) -> "Battle":
        """Создает бой и сохраняет его."""
        player_combatant = create_combatant_from_player(player)
        battle = Battle(player_combatant, opponent_combatant)
        await uow.battles.save(battle)
        return battle
