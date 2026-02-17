from ddd_fantasy_rpg.domain import Battle, CombatantType, PlayerDuelEncounter
from ddd_fantasy_rpg.domain.repositories.player_repository import PlayerRepository
from ddd_fantasy_rpg.domain.repositories.battle_repository import BattleRepository
from ddd_fantasy_rpg.domain.repositories.expedition_repository import ExpeditionRepository


class CompleteBattleUseCase:
    def __init__(
        self,
        player_repository: PlayerRepository,
        battle_repository: BattleRepository,
        expedition_repository: ExpeditionRepository,
    ):
        self._player_repo = player_repository
        self._exp_repo = expedition_repository
        self._battle_repo = battle_repository

    async def execute(self, battle: Battle) -> dict:
        """Завершает бой и возвращает результат."""
        if not battle.is_finished:
            raise ValueError("Battle is not finished")

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
            winner_player = await self._player_repo.get_by_id(winner.id)
            if not winner_player:
                raise ValueError(f"Winner player {winner.id} not found")
            result["winner"] = "player"
        else:
            # Победил монстр — значит, игрок проиграл
            result["winner"] = "monster"
            result["player_died"] = True

        # Загружаем проигравшего (если это игрок)
        loser_player = None
        if loser.combatant_type == CombatantType.PLAYER:
            loser_player = await self._player_repo.get_by_id(loser.id)
            if not loser_player:
                raise ValueError(f"Loser player {loser.id} not found")
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

            await self._player_repo.save(winner_player)

        # === Обработка смерти игрока (проигрыш от монстра) ===
        if result["player_died"] and loser_player:
            # Игрок умирает от монстра — теряет инвентарь
            loser_player.die()
            await self._player_repo.save(loser_player)

        if winner_player:
            exp_winer = await self._exp_repo.get_by_player_id(winner_player.id)
            if not exp_winer:
                raise ValueError("Expedition for winner not found")
            
            exp_winer.complete_with_event(PlayerDuelEncounter(winner_player.id))
            await self._exp_repo.save(exp_winer)
        
        
        if loser_player:
            exp_loser = await self._exp_repo.get_by_player_id(loser_player.id)
            if not exp_loser:
                raise ValueError("Expedition for loser not found")
            
            exp_loser.complete_with_event(PlayerDuelEncounter(loser_player.id))
            await self._exp_repo.save(exp_loser)
        
        
        await self._battle_repo.save(battle)
        return result
