import uuid

from ddd_fantasy_rpg.domain.battle.combatant import Combatant, CombatantType
from ddd_fantasy_rpg.domain.player.player import Player
from ddd_fantasy_rpg.domain.monster.monster import Monster
from ddd_fantasy_rpg.domain.player.character_stats import CharacterStats

def create_combatant_from_player(player: Player) -> Combatant:
    total_stats = player.get_total_stats() 
    max_hp = total_stats.max_hp 
    skills = [] # TODO: Извлечь активные навыки игрока
    return Combatant(
        id=player.id,
        name=player.name,
        combatant_type=CombatantType.PLAYER,
        stats=total_stats,
        max_hp=max_hp,
        skills=skills
    )

def create_combatant_from_monster(monster: Monster) -> Combatant:
    monster_stats = CharacterStats(
        strength=monster.base_damage, 
        agility=5, 
        intelligence=3, 
        max_hp=monster.max_hp,
        damage=monster.base_damage,
        armor=2 
    )
    max_hp = monster_stats.max_hp
    skills = [] # TODO: Извлечь навыки монстра
    return Combatant(
        id=f"monster_{uuid.uuid4()}", 
        name=monster.name,
        combatant_type=CombatantType.MONSTER,
        stats=monster_stats,
        max_hp=max_hp,
        skills=skills
    )