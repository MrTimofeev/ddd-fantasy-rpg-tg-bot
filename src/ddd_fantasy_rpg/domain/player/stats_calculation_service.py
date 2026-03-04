from typing import Dict

from ddd_fantasy_rpg.domain.player.race import Race
from ddd_fantasy_rpg.domain.player.player_profession import PlayerClass

from ddd_fantasy_rpg.domain.player.character_stats import CharacterStats


class StatsCalculationService:
    """Доменный сервис для расчета базовых статов."""
    
    # Базовые статы для всех игроков
    _BASE_STATS: Dict[str, int] = {
        'strength': 10,
        'agility': 8,
        'intelligence': 6,
        'max_hp': 50,
        'damage': 5,
        'armor': 0,
    }

    _RACE_BONUSES: Dict[Race, Dict[str, int]] = {
        Race.HUMAN: {'strength': 1, 'agility': 1, 'intelligence': 1},
        Race.ELF: {'agility': 2, 'intelligence': 1},
        Race.ORC: {'strength': 3, 'max_hp': 10},
        Race.DWARF: {'strength': 2, 'armor': 2},
    }

    _CLASS_BONUSES: Dict[PlayerClass, Dict[str, int]] = {
        PlayerClass.WARRIOR: {'strength': 3, 'max_hp': 15, 'armor': 2},
        PlayerClass.MAGE: {'intelligence': 4, 'damage': 3},
        PlayerClass.ROGUE: {'agility': 3, 'damage': 2},
        PlayerClass.PALADIN: {'strength': 2, 'intelligence': 1, 'max_hp': 10, 'armor': 3},
    }
    
    @classmethod
    def calculate_base_stats(cls, race: Race, profession: PlayerClass) -> CharacterStats:
        stats_dict = cls._BASE_STATS.copy()
        
        race_bonuses = cls._RACE_BONUSES.get(race, {})
        for stat, bonus in race_bonuses.items():
            stats_dict[stat] += bonus
        
        class_bonuses = cls._CLASS_BONUSES.get(profession, {})
        for stat, bonus in class_bonuses.items():
            stats_dict[stat] += bonus
            
        return CharacterStats(**stats_dict)