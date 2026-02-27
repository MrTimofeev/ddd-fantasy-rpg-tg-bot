from typing import Dict

from ddd_fantasy_rpg.domain.player.race import Race
from ddd_fantasy_rpg.domain.player.player_profession import PlayerClass


class StatsCalculationService:
    """Доменный сервис для расчета базовых статов."""
    
    # Базовые статы для всех игроков
    _BASE_STATS = {
        "strength": 10,
        "agility": 10, 
        "intelligence": 10
    }
    
    _RACE_BONUSES: Dict[Race, Dict[str, int]] = {
        Race.HUMAN: {},
        Race.ORC: {"strength":3},
        Race.ELF: {"agility": 2, "intelligence": 1},
        Race.DWARF: {"strength": 2, "agility": -1},
    }
    
    # Бонус по классам
    _CLASS_BONUSES: Dict[PlayerClass, Dict[str, int]] = {
        PlayerClass.WARRIOR: {"strength": 2},
        PlayerClass.MAGE: {"intelligence": 3},
        PlayerClass.ROGUE: {"agility": 3},
        PlayerClass.PALADIN: {"intelligence": 2, "strength": 1}
    }
    
    @classmethod
    def calculate_base_stats(cls, race: Race, progfession: PlayerClass) -> Dict[str, int]:
        """Рассчитываем базовые статы для игрока."""
        stats = cls._BASE_STATS.copy()
        
        # Применяем бонусы расы
        race_bonuses = cls._RACE_BONUSES.get(race, {})
        for stat, bonus in race_bonuses.items():
            stats[stat] += bonus
            
        # Применяем бонусы класса
        class_bonuses = cls._CLASS_BONUSES.get(progfession, {})
        for stat, bonus in class_bonuses.items():
            stats[stat] += bonus
            
        # Убедимся, что статы не уходят в минус
        for stat in stats:
            stats[stat] = max(1, stats[stat])
            
        return stats