from typing import Optional, Dict

from ddd_fantasy_rpg.domain.battle import Battle
from ddd_fantasy_rpg.domain.repositories.battle_repository import BattleRepository


class InMemoryBattleRepository(BattleRepository):
    def __init__(self):
        self._battles: Dict[str, Battle] = {}
        self._player_to_battle: Dict[str, str] = {}

    def save(self, battle: Battle) -> None:
        # Генерируем ID как комбинацию участников
        battle_id = f"{battle._attacker.id}_vs_{battle._defender.id}"
        self._battles[battle_id] = battle
        self._player_to_battle[battle._attacker.id] = battle_id
        self._player_to_battle[battle._defender.id] = battle_id

    def get_by_id(self, battle_id: str) -> Optional[Battle]:
        return self._battles.get(battle_id)

    def get_active_battle_for_player(self, player_id: str) -> Optional[Battle]:
        battle_id = self._player_to_battle.get(player_id)
        if battle_id and battle_id in self._battles:
            battle = self._battles[battle_id]
            if not battle.is_finished:
                return battle
        return None
