from ddd_fantasy_rpg.domain.common.unit_of_work import UnitOfWork
from ddd_fantasy_rpg.domain import Monster, Battle, Player, Combatant
from ddd_fantasy_rpg.domain.battle.combatant_factory import (
    create_combatant_from_player,
    create_combatant_from_monster,
)

from ddd_fantasy_rpg.domain.player import PlayerNotFoundError, PlayerAlreadyInBattleError, SelfDuelError
from ddd_fantasy_rpg.domain.common.notifications import NotificationService



class StartBattleUseCase:
    """
    Use Case для старта битвы
    """

    def __init__(
        self,
        notification_service: NotificationService,
    ):
        self._notification_service = notification_service

    async def start_pve_battle(
        self,
        player: Player,
        monster: Monster,
        uow: UnitOfWork,
    ) -> Battle:
        """Запускает PvE бой (игрок против монстра)."""
        player_combatant = create_combatant_from_player(player)
        opponent_combatant = create_combatant_from_monster(monster)
        await self._notification_service.notify_expedition_complete(
            player_id=player_combatant.id,
            player_hp=player_combatant.current_hp,
            monster_hp=opponent_combatant.current_hp,
            monster_level=monster.level,
            monster_name=monster.name,
        )
        return await self._create_battle(player_combatant, opponent_combatant, uow)

    async def start_pvp_battle(
        self,
        player1_id: str,
        player2_id: str,
        uow: UnitOfWork
    ) -> Battle:
        """Запускает PvP дуэль (игрок против игрока)."""
        # TODO: Добавить уведомление игроку
        player1 = await self._load_player(player1_id, uow)
        player2 = await self._load_player(player2_id, uow)
        
        if player1_id == player2_id:
            raise SelfDuelError()
        
        player_combatant = create_combatant_from_player(player1)
        opponent_combatant = create_combatant_from_player(player2)
        
        await self._notification_service.notify_pvp_match_found(player1, player2)
        return await self._create_battle(player_combatant, opponent_combatant, uow)
        
        
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
        player_combatant: "Combatant",
        opponent_combatant: "Combatant",
        uow: UnitOfWork,
    ) -> "Battle":
        """Создает бой и сохраняет его."""
        battle = Battle(player_combatant, opponent_combatant)
        await uow.battles.save(battle)
        return battle
