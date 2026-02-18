from typing import Union

from ddd_fantasy_rpg.domain.unit_of_work import UnitOfWork
from ddd_fantasy_rpg.domain import Monster, Battle
from ddd_fantasy_rpg.domain.combatant_factory import (
    create_combatant_from_player,
    create_combatant_from_monster,
)

from ddd_fantasy_rpg.domain.exceptions import PlayerNotFoundError, PlayerAlreadyInBattleError


class StartBattleUseCase:
    """
    Use Case для старта битвы
    """

    async def execute(
        self,
        player_id: str,
        opponent: Union[Monster, str],  # str = opponent_player_id (для PVP)
        uow: UnitOfWork
    ) -> Battle:
        # 1. Загружаем игрока
        player = await uow.players.get_by_id(player_id)
        if not player:
            raise PlayerNotFoundError(player_id)

        # 2. Проверяем, нет ли активного боя
        active_battle = await uow.battles.get_active_battle_for_player(player_id)
        if active_battle:
            raise PlayerAlreadyInBattleError(player_id)

        # 3. Создаем Combatan'ов
        player_combatant = create_combatant_from_player(player)

        if isinstance(opponent, Monster):
            opponent_combatant = create_combatant_from_monster(opponent)
        else:
            opponent_player = await uow.players.get_by_id(opponent)
            if not opponent_player:
                raise PlayerNotFoundError()
            opponent_combatant = create_combatant_from_player(opponent_player)

        # 4. Создаем бой
        battle = Battle(player_combatant, opponent_combatant)

        # 5. Сохряняем
        await uow.battles.save(battle)

        return battle
