from ddd_fantasy_rpg.domain.expedition.expedition_distance import ExpeditionDistance
from ddd_fantasy_rpg.domain.expedition.expedition_event import ExpeditionEvent, MonsterEncounter, PlayerDuelEncounter, TraderEncounter, ResourceGathering

from ddd_fantasy_rpg.domain.monster.monster import Monster
from ddd_fantasy_rpg.domain.items.item_instance import ItemInstance
from ddd_fantasy_rpg.domain.items.item_type import ItemType
from ddd_fantasy_rpg.domain.items.item_stats import ItemStats
from ddd_fantasy_rpg.domain.items.item_rarity import Rarity
from ddd_fantasy_rpg.domain.common.random_provider import RandomProvider

def generate_monster_for_distance(distance: ExpeditionDistance, random_provider: RandomProvider) -> Monster:
    
    monster_names = ["Goblin", "Orc", "Skeleton", "Spider"]
    name = random_provider.choice(monster_names)
    
    level = random_provider.randint(1, 3) + distance.value[1]
    
    return Monster(
        name=name,
        level=level,
        base_damage=5,
        max_hp=50,
        drop_items=[],
        flee_difficulty=1,
    )
    
def generate_item_for_rarity(rarity: str, random_provider: RandomProvider):
    pass

class ExpeditionEventGenerator:
    def __init__(self, random_provider: RandomProvider):
        self._random_provider = random_provider
        
    def generate_event(self, distance: ExpeditionDistance) -> 'ExpeditionEvent':
        event_weights = {
            'moster': 40,
            'trader': 20,
            'resource': 20,
            'pvp': 10,
        }
        
        event_type = self._random_provider.choices(list(event_weights.keys()), weights=event_weights.values(), k=1)[0]

        if event_type == 'monster':
            monster = generate_monster_for_distance(distance, self._random_provider)
            return MonsterEncounter(monster=monster)
        elif event_type == 'trader':
            return TraderEncounter()
        elif event_type == 'resource':
            resource_type = self._random_provider.choice(["wood", "ore", "herbs"])
            amount = self._random_provider.randint(1, 5)
            return ResourceGathering(resource_type=resource_type, amount=amount)
        elif event_type == "pvp":
            return PlayerDuelEncounter(opponent_player_id=None)
        else:    
            return MonsterEncounter(monster=generate_monster_for_distance(distance, self._random_provider))
        

            