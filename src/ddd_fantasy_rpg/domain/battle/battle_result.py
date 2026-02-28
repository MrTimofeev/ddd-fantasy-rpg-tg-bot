from dataclasses import dataclass
from typing import List

from ddd_fantasy_rpg.domain.items.item import Item

@dataclass(frozen=True)
class BattleParticipant:
    """Участник боя."""
    id: str
    is_player: bool
    is_monster: bool
    
    @property
    def is_alive(self) -> bool:
        # В бою все участники alive, но после боя может быть иначе
        return True
    

@dataclass(frozen=True)
class BattleOutcome:
    """Результат боя."""
    pass

@dataclass(frozen=True)
class PlayerVictory(BattleOutcome):
    """Победа игрока."""
    winner: BattleParticipant
    loser: BattleParticipant
    loot: List[Item]
    experience_gained: int
    

@dataclass(frozen=True)
class MonsterVictory(BattleOutcome):
    """Победа монстра(поражение игрока)."""
    winner: BattleParticipant # монстр
    loser: BattleParticipant  # игрок
    

@dataclass(frozen=True)
class PvpVictory(BattleOutcome):
    """Победа в PvP дуэли."""
    winner: BattleParticipant
    loser: BattleParticipant
    loot: list[Item]
    
@dataclass(frozen=True)
class BattleResult:
    """Полный результат боя."""
    outcome: BattleOutcome
    is_pvp: bool