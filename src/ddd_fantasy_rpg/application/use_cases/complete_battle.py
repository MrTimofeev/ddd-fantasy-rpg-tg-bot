from ddd_fantasy_rpg.domain.unit_of_work import UnitOfWork
from ddd_fantasy_rpg.domain import Battle, CombatantType, PlayerDuelEncounter
from ddd_fantasy_rpg.domain.exceptions import BattleAlreadyFinishedError, ExpeditionNotFoundError, PlayerNotFoundError



class CompleteBattleUseCase:
    """
    Use Case для заверешния битвы. 
    """

    async def execute(self, battle: Battle, uow: UnitOfWork) -> dict:
        """Завершает бой и возвращает результат."""
        if not battle.is_finished:
            raise BattleAlreadyFinishedError()

        # Определяем победителя и проигравшего
        winner = battle.winner
        loser = (
            battle._defender if battle._attacker.id == winner.id else battle._attacker
        )

        result = {
            "winner": None,
            "loot": [],
            "player_died": False,
            "is_pvp": False
        }

        # Загружаем победителя (если это игрок)
        winner_player = None
        if winner.combatant_type == CombatantType.PLAYER:
            winner_player = await uow.players.get_by_id(winner.id)
            if not winner_player:
                raise PlayerNotFoundError(winner.id)
            result["winner"] = "player"
        else:
            # Победил монстр — значит, игрок проиграл
            result["winner"] = "monster"
            result["player_died"] = True

        # Загружаем проигравшего (если это игрок)
        loser_player = None
        if loser.combatant_type == CombatantType.PLAYER:
            loser_player = await uow.players.get_by_id(loser.id)
            if not loser_player:
                raise PlayerNotFoundError(loser.id)
            result["is_pvp"] = (winner.combatant_type == CombatantType.PLAYER)

        # === Обработка победы игрока ===
        if winner_player:
            # Начисление опыта (только за монстров)
            if loser.combatant_type == CombatantType.MONSTER:
                exp_gain = loser.stats.max_hp * 2
                # TODO: обновить уровень игрока

            # Выпадение лута
            # if hasattr(loser, "drop_items"):
            #     result["loot"] = loser.drop_items

            # В PvP: победитель получает инвентарь проигравшего
            if result["is_pvp"] and loser_player:
                for item in loser_player.inventory:
                    winner_player.add_item(item)
                # Очищаем инвентарь проигравшего
                loser_player.die()  

            await uow.players.save(winner_player)

        # === Обработка смерти игрока (проигрыш от монстра) ===
        if result["player_died"] and loser_player:
            # Игрок умирает от монстра — теряет инвентарь
            loser_player.die()
            await uow.players.save(loser_player)

        if winner_player:
            exp_winer = await uow.expeditions.get_by_player_id(winner_player.id)
            if not exp_winer:
                raise ExpeditionNotFoundError(winner_player.id)
            
            exp_winer.complete_with_event(PlayerDuelEncounter(winner_player.id))
            await uow.expeditions.save(exp_winer)
        
        
        if loser_player:
            exp_loser = await uow.expeditions.get_by_player_id(loser_player.id)
            if not exp_loser:
                raise ExpeditionNotFoundError(loser_player.id)
            
            exp_loser.complete_with_event(PlayerDuelEncounter(loser_player.id))
            await uow.expeditions.save(exp_loser)
        
        
        await uow.battles.save(battle)
        return result
