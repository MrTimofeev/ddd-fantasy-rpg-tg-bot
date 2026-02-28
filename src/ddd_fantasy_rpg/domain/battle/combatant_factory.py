import uuid

from ddd_fantasy_rpg.domain.player import Player, PlayerClass
from ddd_fantasy_rpg.domain.monster.monster import Monster
from ddd_fantasy_rpg.domain.battle.combatant import Combatant, CombatantType, CombatantStats
from ddd_fantasy_rpg.domain.skills.skill import Skill, SkillType


def create_combatant_from_player(player: Player) -> Combatant:
    # TODO: Добавить бонусы от экипировки
    # Собираем статы

    stats = player.get_total_stats()
    max_hp = 50 + (player.level * 10)

    skills = []
    if player._profession == PlayerClass.WARRIOR:
        skills = [
            Skill("Cleave", SkillType.DAMAGE,
                  base_power=15, cooldown_turns=2),
            Skill("Battle Cry", SkillType.BUFF,
                  base_power=5, cooldown_turns=4),
        ]
    elif player._profession == PlayerClass.MAGE:
        skills = [
            Skill("Fireball", SkillType.DAMAGE,
                  base_power=20, cooldown_turns=3),
            Skill("Heal", SkillType.HEAL, base_power=25, cooldown_turns=4),
        ]

    return Combatant(
        id=player.id,
        name=player._name,
        combatant_type=CombatantType.PLAYER,
        stats=CombatantStats(
            strength=stats.get("strength", 10),
            agility=stats.get("agility", 10),
            intelligence=stats.get("intelligence", 10),
            max_hp=max_hp,
        ),
        _current_hp=max_hp,
        skills=skills,
    )
    
def create_combatant_from_monster(monster: Monster) -> Combatant:
    return Combatant(
        id=str(uuid.uuid4()),
        name=monster.name,
        combatant_type=CombatantType.MONSTER,
        stats=CombatantStats(
            strength=monster.base_damage,
            agility= monster.level,
            intelligence=1,
            max_hp=monster.max_hp,
        ),
        _current_hp=monster.max_hp,
        skills=[], # TODO: монстры пока без скиллов
    )
