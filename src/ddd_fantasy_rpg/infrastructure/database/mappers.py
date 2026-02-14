from typing import Optional
from datetime import timezone

from ddd_fantasy_rpg.domain import Player, Expedition
from ddd_fantasy_rpg.domain.battle import Battle
from ddd_fantasy_rpg.infrastructure.database.models import PlayerORM, ExpeditionORM, BattleORM
from ddd_fantasy_rpg.infrastructure.database.dto import ItemDTO


# === Player Mapper ===
def player_to_orm(player: Player) -> PlayerORM:
    inventory_dto = [
        ItemDTO(
            id=item.id,
            name=item.name,
            item_type=item.item_type.value,
            level_required=item.level_required,
            rarity=item.rarity,
            stats=item.stats.__dict__,
        ).to_dict()
        for item in player.inventory
    ]
    equipped_dto = {}
    for slot, item in player._equipped.items():
        dto = ItemDTO(
            id=item.id,
            name=item.name,
            item_type=item.item_type.value,
            level_required=item.level_required,
            rarity=item.rarity,
            stats=item.stats.__dict__,
        )
        equipped_dto[slot] = dto.to_dict()

    return PlayerORM(
        id=player.id,
        telegram_id=player._telegram_id,
        name=player._name,
        race=player._race.value,
        player_class=player._class.value,
        level=player._level,
        exp=player._exp,
        inventory=inventory_dto,
        equipped=equipped_dto,
        is_on_expedition=player.is_on_expedition,
    )


def player_from_orm(orm: PlayerORM) -> Player:
    data = {
        "id": orm.id,
        "telegram_id": orm.telegram_id,
        "name": orm.name,
        "race": orm.race,
        "player_class": orm.player_class,
        "level": orm.level,
        "exp": orm.exp,
        "is_on_expedition": orm.is_on_expedition,
        "inventory": orm.inventory or [],
    }
    return Player.from_dict(data)


# === Expedition Mapper ===
def expedition_to_orm(expedition: Expedition) -> ExpeditionORM:
    outcome_type = None
    outcome_data = None
    if expedition.outcome:
        if hasattr(expedition.outcome, "monster"):
            outcome_type = "monster"
            outcome_data = {
                "monster": {
                    "id": expedition.outcome.monster.id,
                    "name": expedition.outcome.monster.name,
                    "level": expedition.outcome.monster.level,
                    "base_damage": expedition.outcome.monster.base_damage,
                    "max_hp": expedition.outcome.monster.max_hp,
                    "drop_items": [
                        {
                            "id": item.id,
                            "name": item.name,
                            "item_type": item.item_type.value,
                            "level_required": item.level_required,
                            "rarity": item.rarity,
                            "stats": item.stats.__dict__,
                        }
                        for item in expedition.outcome.monster.drop_items
                    ],
                    "flee_difficulty": expedition.outcome.monster.flee_difficulty,
                }
            }

    return ExpeditionORM(
        player_id=expedition.player_id,
        distance=expedition.distance.key,
        start_time=expedition.start_time,
        end_time=expedition.end_time,
        outcome_type=outcome_type,
        outcome_data=outcome_data,
    )


def expedition_from_orm(orm: ExpeditionORM) -> Optional[Expedition]:
    if not orm:
        return None

    start_time = orm.start_time
    end_time = orm.end_time

    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=timezone.utc)

    # Восстанавливаем distance
    from ddd_fantasy_rpg.domain import ExpeditionDistance
    distance = next(d for d in ExpeditionDistance if d.key == orm.distance)

    # Восстанавливаем событие
    outcome = None
    if orm.outcome_type == "monster" and orm.outcome_data:
        from ddd_fantasy_rpg.domain import Monster, Item, ItemType, ItemStats
        mob_data = orm.outcome_data["monster"]
        drop_items = [
            Item(
                id=item["id"],
                name=item["name"],
                item_type=ItemType(item["item_type"]),
                level_required=item["level_required"],
                rarity=item["rarity"],
                stats=ItemStats(**item["stats"]),
            )
            for item in mob_data["drop_items"]
        ]
        monster = Monster(
            id=mob_data["id"],
            name=mob_data["name"],
            level=mob_data["level"],
            base_damage=mob_data["base_damage"],
            max_hp=mob_data["max_hp"],
            drop_items=drop_items,
            flee_difficulty=mob_data["flee_difficulty"],
        )
        from ddd_fantasy_rpg.domain.expedition import MonsterEncounter
        outcome = MonsterEncounter(monster=monster)

    return Expedition(
        player_id=orm.player_id,
        distance=distance,
        start_time=start_time,
        end_time=end_time,
        outcome=outcome,
    )
    
def serialize_combatant(combatant: "Combatant") -> dict:
    return {
        "id": combatant.id,
        "name": combatant.name,
        "combatant_type": combatant.combatant_type.value,  
        "stats": combatant.stats.__dict__,
        "current_hp": combatant.current_hp,
        "skills": [], 
    }


def deserialize_combatant(data: dict) -> "Combatant":
    from ddd_fantasy_rpg.domain.battle import Combatant, CombatantStats, CombatantType
    return Combatant(
        id=data["id"],
        name=data["name"],
        combatant_type=CombatantType(data["combatant_type"]),
        stats=CombatantStats(**data["stats"]),
        current_hp=data["current_hp"],
        skills=[], 
    )
    
# === Battele Mapper ===
def battle_to_orm(battle: Battle):
    battle_id = f"{battle._attacker.id}_vs_{battle._defender.id}"
    return BattleORM(
        id=battle_id,
        attacker_id=battle._attacker.id,
        defender_id=battle._defender.id,
        attacker_data=serialize_combatant(battle._attacker),
        defender_data=serialize_combatant(battle._defender),
        current_turn_owner_id=battle._current_turn_owner_id,
        is_finished=battle.is_finished,
        winner_id=battle.winner.id if battle.winner else None,
    )

def battle_from_orm(orm: BattleORM) -> Optional[Battle]:
    if not orm:
        return None

    attacker = deserialize_combatant(orm.attacker_data)
    defender = deserialize_combatant(orm.defender_data)
    
    battle = Battle(attacker, defender)
    battle._current_turn_owner_id = orm.current_turn_owner_id
    battle._is_finished = orm.is_finished
    battle._winner = attacker if orm.winner_id == attacker.id else defender if orm.winner_id else None
    return battle


