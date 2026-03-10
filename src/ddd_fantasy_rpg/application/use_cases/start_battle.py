import uuid
from typing import Callable

from ddd_fantasy_rpg.domain.common.unit_of_work import UnitOfWork
from ddd_fantasy_rpg.domain.common.random_provider import RandomProvider
from ddd_fantasy_rpg.domain.monster.monster import Monster
from ddd_fantasy_rpg.domain.battle.battle import Battle
from ddd_fantasy_rpg.domain.player.player import Player
from ddd_fantasy_rpg.domain.battle.combatant_factory import (
    create_combatant_from_player,
    create_combatant_from_monster,
)

from ddd_fantasy_rpg.domain.player.exceptions import PlayerNotFoundError, PlayerAlreadyInBattleError, SelfDuelError
from ddd_fantasy_rpg.domain.common.notifications import NotificationService
from ddd_fantasy_rpg.application.events.dispatcher import EventDispatcher


class StartBattleUseCase:
    """
    Use Case для старта битвы
    """

    def __init__(
        self,
        random_provider: RandomProvider,
        dispatcher: EventDispatcher,
        notification_service: NotificationService,
        uow_factory: Callable[[], UnitOfWork],
    ):
        self._random_provider = random_provider
        self._dispatcher = dispatcher
        self._notification_service = notification_service
        self._uow_factory = uow_factory

    async def start_pve_battle(
        self,
        player: Player,
        monster: Monster,
    ) -> Battle:
        """Запускает PvE бой (игрок против монстра)."""
        async with self._uow_factory() as uow:
            active_battle = await uow.battles.get_active_battle_for_player(player.id)
            if active_battle:
                raise PlayerAlreadyInBattleError(player.id)

            player_combatant = create_combatant_from_player(player)
            opponent_combatant = create_combatant_from_monster(monster)

            battle_id = str(uuid.uuid4())

            battle = Battle.start(
                battle_id, player_combatant, opponent_combatant, self._random_provider)
            await uow.battles.save(battle)
            event_to_publish = battle.pop_pending_events()

        if event_to_publish:
            await self._dispatcher.publish(event_to_publish)

        return battle

    async def start_pvp_battle(
        self,
        player1_id: str,
        player2_id: str,
    ) -> Battle:
        """Запускает PvP дуэль (игрок против игрока)."""
        async with self._uow_factory() as uow:
            player1 = await self._load_player(player1_id, uow)
            player2 = await self._load_player(player2_id, uow)

            if player1_id == player2_id:
                raise SelfDuelError()

            player1_combatant = create_combatant_from_player(player1)
            player2_combatant = create_combatant_from_player(player2)

            battle_id = str(uuid.uuid4())

            battle = Battle.start(
                battle_id, player1_combatant, player2_combatant, self._random_provider)
            await uow.battles.save(battle)

            event_to_publish = battle.pop_pending_events()

        if event_to_publish:
            await self._dispatcher.publish(event_to_publish)

        return battle

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
