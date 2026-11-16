from typing import Callable, Optional

from ddd_fantasy_rpg.domain.common.unit_of_work import UnitOfWork
from ddd_fantasy_rpg.domain.battle.battle import Battle
from ddd_fantasy_rpg.domain.battle.battle_result import BattleResult, PlayerVictory, MonsterVictory, PvpVictory
from ddd_fantasy_rpg.domain.battle.exceptions import BattleAlreadyFinishedError, BattleNotFoundError
from ddd_fantasy_rpg.domain.items.item_instance import ItemInstance
from ddd_fantasy_rpg.domain.player.exceptions import PlayerNotFoundError
from ddd_fantasy_rpg.application.events.dispatcher import EventDispatcher


class CompleteBattleUseCase:
    """
    Use Case для заверешния битвы. 
    """

    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        dispatcher: EventDispatcher,
    ):
        self._uow_factory = uow_factory
        self._dispatcher = dispatcher

    async def complete_pve_battle(
        self,
        battle_id: str,
        monster_drop_loot: Optional[list[ItemInstance]] = None
    ) -> BattleResult:
        """Завершает PVE бой (игрок vs монстр)"""
        async with self._uow_factory() as uow:
            battle = await uow.battles.get_by_id(battle_id)
            if not battle:
                raise BattleAlreadyFinishedError()

            result = battle.get_battle_result()
            if not result:
                raise ValueError("Результат у боя должен быть")
            
            outcome = result.outcome
            player = None

            if isinstance(outcome, PlayerVictory):
                player = await uow.players.get_by_id(outcome.winner.id)
                if not player:
                    raise PlayerNotFoundError(outcome.winner.id)

                # Начисление опыта и лута
                player.add_exp(outcome.experience_gained)
                
                if monster_drop_loot:
                    for item in monster_drop_loot:
                        player.add_item_to_inventory(item)

            elif isinstance(outcome, MonsterVictory):
                player = await uow.players.get_by_id(outcome.loser.id)
                if not player:
                    raise PlayerNotFoundError(outcome.loser.id)

                player.die(killer_id=None)

            else:
                raise ValueError(f'неизвестный исход боя: {type(outcome)}')
            
            await uow.players.save(player)
            
            # Обновляем экспедицию игрока
            expedition = await uow.expeditions.get_by_player_id(player.id)
            if expedition:
                expedition.set_complete_event_status()
                await uow.expeditions.save(expedition)

            await uow.battles.save(battle)
            
            # Сбор событий со всех агрегатов
            events_to_publish = []
            events_to_publish.extend(player.pop_pending_events())   
            events_to_publish.extend(battle.pop_pending_events())
        
        if events_to_publish:
            await self._dispatcher.publish(events_to_publish)
            
        return result

    async def complete_pvp_battle(
        self,
        battle_id: str,
    ) -> BattleResult:
        """Завершаем PVP дуэаль (игрок vs игрок)."""
        async with self._uow_factory() as uow:
            battle = await uow.battles.get_by_id(battle_id)
            
            if not battle:
                raise BattleNotFoundError(battle_id)
            
            if not battle.is_finished:
                raise BattleAlreadyFinishedError()

            result = battle.get_battle_result()
            if not result:
                raise ValueError("Результат у боя должен быть")
            outcome = result.outcome

            if not isinstance(outcome, PvpVictory):
                raise ValueError("Expected PvpVictory outcome")

            winner = await uow.players.get_by_id(outcome.winner.id)
            loser = await uow.players.get_by_id(outcome.loser.id)

            if not winner:
                raise PlayerNotFoundError(outcome.winner.id)
            if not loser:
                raise PlayerNotFoundError(outcome.loser.id)

            # переносим инвентарь проигравшего
            dropped_items = loser.die(killer_id=winner.id)
            
            for item in dropped_items:
                item.owner_id = winner.id
                winner.add_item_to_inventory(item)

            winner.add_exp(outcome.experience_gained)

            await uow.players.save(winner)
            await uow.players.save(loser)

            # Обновляем экспедиции обоих игроков
            for player in [winner, loser]:
                expedition = await uow.expeditions.get_by_player_id(player.id)
                if expedition:
                    expedition.set_complete_event_status()
                    await uow.expeditions.save(expedition)

            await uow.battles.save(battle)
            
            # Сбор событий
            event_to_publish = []
            event_to_publish.extend(winner.pop_pending_events())
            event_to_publish.extend(loser.pop_pending_events())
            event_to_publish.extend(battle.pop_pending_events())

        if event_to_publish:
            await self._dispatcher.publish(event_to_publish)
            
        return result