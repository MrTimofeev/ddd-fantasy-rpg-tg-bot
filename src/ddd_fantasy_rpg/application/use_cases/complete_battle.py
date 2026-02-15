from ddd_fantasy_rpg.domain import Battle
from ddd_fantasy_rpg.domain.repositories.player_repository import PlayerRepository
from ddd_fantasy_rpg.domain.repositories.battle_repository import BattleRepository


class CompleteBattleUseCase:
    def __init__(self, player_repository: PlayerRepository, battle_repository: BattleRepository):
        self._player_repo = player_repository
        self._battle_repo = battle_repository

    async def execute(self, battle: Battle) -> dict:
        """Завершает бой и возврашает результат."""

        if not battle.is_finished:
            raise ValueError("Battle is not finished")

        result = {"winner": None, "loot": [], "player_died": False}

        player = None
        oppnent = None

        # Определяем, кто игрок, а кто противник
        if battle.winner.combatant_type.value == "player":
            player = await self._player_repo.get_by_id(battle.winner.id)
            opponent = battle._defender if battle._attacker.id == player.id else battle._attacker
            result["winner"] = "player"
        else:
            player = await self._player_repo.get_by_id(
                battle._defender.id if battle._attacker.combatant_type.value == "monster" else battle._attacker.id
            )
            result["winner"] = "monster"
            result["player_died"] = True

        if not player:
            raise ValueError("Play not found")

        if result["winner"] == "player":
            exp_gain = opponent.stats.max_hp * 2
            # TODO: обновить уровнь игрока

            if hasattr(opponent, "drop_items"):
                # TODO: сделать выпадение предметов
                pass

            await self._player_repo.save(player)

        elif result["player_died"]:
            # Игрок умирает - теряет инвентарь
            player.die()
            await self._player_repo.save(player)

        await self._player_repo.save(player)
        await self._battle_repo.save(battle)

        return result
