from ddd_fantasy_rpg.domain.unit_of_work import UnitOfWork
from ddd_fantasy_rpg.domain import Battle, CombatantType, PlayerDuelEncounter
from ddd_fantasy_rpg.domain.battle_result import BattleResult, PlayerVictory, MonsterVictory, PvpVictory
from ddd_fantasy_rpg.domain.exceptions import BattleAlreadyFinishedError, PlayerNotFoundError


class CompleteBattleUseCase:
    """
    Use Case для заверешния битвы. 
    """

    async def complete_pve_battle(
        self,
        battle: Battle,
        uow: UnitOfWork,
    ) -> BattleResult:
        """Завершает PVE бой (игрок vs монстр)"""

        if not battle.is_finished:
            raise BattleAlreadyFinishedError()

        result = battle.get_battle_result()
        outcome = result.outcome

        # только один игрок учасвствует в PVE
        player_id = self._get_player_id_from_outcome(outcome)
        player = await uow.players.get_by_id(player_id)
        if not player:
            raise PlayerNotFoundError(player_id)

        if isinstance(outcome, PlayerVictory):
            # Начисление опыта и лута
            exp_gain = self._calculate_experience(
                outcome.loser)  # TODO: реализовать
            loot = self._generate_loot(outcome.loser)  # TODO: реализовать

            update_outcome = PlayerVictory(
                winner=outcome.winner,
                loser=outcome.loser,
                loot=loot,
                experience_gained=exp_gain
            )

            result = BattleResult(outcome=update_outcome, is_pvp=False)

            # применяем изменени к игроку
            # TODO: добавляем опыт (player.add_experience(exp_gain))
            # TODO: добавляем лут (plaery.add_item(item))

            await uow.players.save(player)

        elif isinstance(outcome, MonsterVictory):
            # Игрок погиб
            player.die()
            await uow.players.save(player)

        # Обновляем экспедицию игрока
        expedition = await uow.expeditions.get_by_player_id(player.id)
        if expedition:
            expedition.complete_with_event(PlayerDuelEncounter(player.id))

        await uow.battles.save(battle)
        return result

    async def complete_pvp_battle(
        self,
        battle: Battle,
        uow: UnitOfWork
    ) -> BattleResult:
        """Завершаем PVP дуэаль (игрок vs игрок)."""
        if not battle.is_finished:
            raise BattleAlreadyFinishedError()

        result = battle.get_battle_result()
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
        loot = list(loser.inventory)
        for item in loot:
            winner.add_item(item)

        loser.die()

        update_outcome = PvpVictory(
            winner=outcome.winner,
            loser=outcome.loser,
            loot=loot
        )

        result = BattleResult(outcome=update_outcome, is_pvp=True)

        await uow.players.save(winner)
        await uow.players.save(loser)

        # Обновляем экспедиции обоих игроков
        for player in [winner, loser]:
            expedition = await uow.expeditions.get_by_player_id(player.id)
            if expedition:
                expedition.complete_with_event(PlayerDuelEncounter(player.id))
                await uow.expeditions.save(expedition)

        await uow.battles.save(battle)
        return result

    def _get_player_id_from_outcome(self, outcome) -> str:
        """Возвращает ID игрока из ихода боя (для PVE)."""
        if outcome.winner.is_player:
            return outcome.winner.id
        elif outcome.loser.is_player:
            return outcome.loser.id
        else:
            raise ValueError("No player found is battle outcome")

    def _calculate_experience(self, monster_participant) -> int:
        # TODO: реализовать логику начисление опыта
        return 0

    def _generate_loot(self, monster_participant) -> list:
        # TODO: реализовать генерацию лута
        return []
