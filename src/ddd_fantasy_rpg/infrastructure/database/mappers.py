from typing import Optional, Dict, Any
from datetime import timezone

from ddd_fantasy_rpg.domain import (
    Player, Race, PlayerClass,
    Expedition, ExpeditionDistance, PlayerDuelEncounter, ExpeditionStatus,
    Item, 
    Battle, ItemType, ItemStats, Combatant, CombatantType, CombatantStats,
    Monster, MonsterEncounter
    )
from ddd_fantasy_rpg.infrastructure.database.models import PlayerORM, ExpeditionORM, BattleORM

# === Вспомогательные функции для Item ===
def _item_to_dict(item: Item) -> Dict[str, Any]:
    return {
        "name": item.name,
        "item_type": item.item_type.value,
        "level_required": item.level_required,
        "rarity": item.rarity.value if hasattr(item.rarity, 'value') else item.rarity,
        "stats": {
            "strength": item.stats.strength,
            "agility": item.stats.agility,
            "intelligence": item.stats.intelligence,
            "max_hp": item.stats.max_hp,
            "damage": item.stats.damage,
        }
    }


def _item_from_dict(data: Dict[str, Any]) -> Item:
    return Item(
        name=data["name"],
        item_type=ItemType(data["item_type"]),
        level_required=data["level_required"],
        rarity=data["rarity"],  # если Rarity(Enum) — будет int
        stats=ItemStats(
            strength=data["stats"]["strength"],
            agility=data["stats"]["agility"],
            intelligence=data["stats"]["intelligence"],
            max_hp=data["stats"]["max_hp"],
            damage=data["stats"]["damage"],
        )
    )


# === Player Mapper ===
def player_to_orm(player: Player) -> PlayerORM:
    inventory_data = [_item_to_dict(item) for item in player.inventory]

    equipped_data = {}
    for slot, item in player._equipped.items():
        equipped_data[slot] = _item_to_dict(item)

    return PlayerORM(
        id=player.id,
        telegram_id=player._telegram_id,
        name=player._name,
        race=player._race.value,
        player_profession=player._profession.value,
        level=player._level,
        exp=player._exp,
        inventory=inventory_data,
        equipped=equipped_data,
    )


def player_from_orm(orm: PlayerORM) -> Player:
    inventory = [_item_from_dict(item_data)
                 for item_data in (orm.inventory or [])]

    equipped = {}
    for slot, item_data in (orm.equipped or {}).items():
        equipped[slot] = _item_from_dict(item_data)

    player = Player.__new__(Player)
    player._id = orm.id
    player._telegram_id = orm.telegram_id
    player._name = orm.name
    player._race = Race(orm.race)
    player._profession = PlayerClass(orm.player_profession)
    player._level = orm.level
    player._exp = orm.exp
    player._inventory = inventory
    player._equipped = equipped
    player._base_stats = player._calculate_base_stats()
    return player


# === Combatant Mapper (для Battle) ===
def _combatant_to_dict(combatant: Combatant) -> Dict[str, Any]:
    return {
        "id": combatant.id,
        "name": combatant.name,
        "combatant_type": combatant.combatant_type.value,
        "stats": {
            "strength": combatant.stats.strength,
            "agility": combatant.stats.agility,
            "intelligence": combatant.stats.intelligence,
            "max_hp": combatant.stats.max_hp,
        },
        "current_hp": combatant.current_hp,
        "skills": []  # TODO: сериализация скиллов
    }


def _combatant_from_dict(data: Dict[str, Any]) -> Combatant:
    return Combatant(
        id=data["id"],
        name=data["name"],
        combatant_type=CombatantType(data["combatant_type"]),
        stats=CombatantStats(
            strength=data["stats"]["strength"],
            agility=data["stats"]["agility"],
            intelligence=data["stats"]["intelligence"],
            max_hp=data["stats"]["max_hp"],
        ),
        _current_hp=data["current_hp"],
        skills=[]  # TODO: десериализация скиллов
    )


# === Expedition Mapper ===
def expedition_to_orm(expedition: Expedition) -> ExpeditionORM:
    outcome_type = None
    outcome_data = None

    if expedition.outcome and isinstance(expedition.outcome, MonsterEncounter):
        monster = expedition.outcome.monster
        outcome_type = "monster"
        outcome_data = {
            "monster": {
                "name": monster.name,
                "level": monster.level,
                "base_damage": monster.base_damage,
                "max_hp": monster.max_hp,
                "drop_items": [_item_to_dict(item) for item in monster.drop_items],
                "flee_difficulty": monster.flee_difficulty,
            }
        }
    elif expedition.outcome and isinstance(expedition.outcome, PlayerDuelEncounter):
        outcome_type = "pvp"
        outcome_data = {
            "opponent_player_id": expedition.outcome.opponent_player_id
        }

    return ExpeditionORM(
        id=expedition.id,
        player_id=expedition.player_id,
        distance=expedition.distance.key,
        start_time=expedition.start_time,
        end_time=expedition.end_time,
        outcome_type=outcome_type,
        outcome_data=outcome_data,
        status=expedition.status.value,
    )


def expedition_from_orm(orm: ExpeditionORM) -> Optional[Expedition]:
    if not orm:
        return None

    # Обработка временных зон
    start_time = orm.start_time.replace(
        tzinfo=timezone.utc) if orm.start_time.tzinfo is None else orm.start_time
    end_time = orm.end_time.replace(
        tzinfo=timezone.utc) if orm.end_time.tzinfo is None else orm.end_time

    # Восстановление distance
    distance = next(d for d in ExpeditionDistance if d.key == orm.distance)

    # Восстановление события
    outcome = None
    if orm.outcome_type == "monster" and orm.outcome_data:
        mob_data = orm.outcome_data["monster"]
        drop_items = [_item_from_dict(item) for item in mob_data["drop_items"]]
        monster = Monster(  
            name=mob_data["name"],
            level=mob_data["level"],
            base_damage=mob_data["base_damage"],
            max_hp=mob_data["max_hp"],
            drop_items=drop_items,
            flee_difficulty=mob_data["flee_difficulty"],
        )
        outcome = MonsterEncounter(monster=monster)
    elif orm.outcome_type == "pvp" and orm.outcome_data:
        outcome = PlayerDuelEncounter(
            opponent_player_id=orm.outcome_data["opponent_player_id"]
        )

    return Expedition(
        id=orm.id,
        player_id=orm.player_id,
        distance=distance,
        start_time=start_time,
        end_time=end_time,
        outcome=outcome,
        status=ExpeditionStatus(orm.status), 
    )


# === Battle Mapper ===
def battle_to_orm(battle: Battle) -> BattleORM:
    battle_id = f"{battle._attacker.id}_vs_{battle._defender.id}"
    return BattleORM(
        id=battle_id,
        attacker_id=battle._attacker.id,
        defender_id=battle._defender.id,
        attacker_data=_combatant_to_dict(battle._attacker),
        defender_data=_combatant_to_dict(battle._defender),
        current_turn_owner_id=battle._current_turn_owner_id,
        is_finished=battle.is_finished,
        winner_id=battle.winner.id if battle.winner else None,
    )


def battle_from_orm(orm: BattleORM) -> Optional[Battle]:
    if not orm:
        return None

    attacker = _combatant_from_dict(orm.attacker_data)
    defender = _combatant_from_dict(orm.defender_data)
    winner = None
    if orm.winner_id:
        winner = attacker if orm.winner_id == attacker.id else defender

    # Используем фабричный метод для обхода проверки is_alive
    battle = Battle.__new__(Battle)
    battle._attacker = attacker
    battle._defender = defender
    battle._current_turn_owner_id = orm.current_turn_owner_id
    battle._is_finished = orm.is_finished
    battle._winner = winner
    battle._flee_attempts = {attacker.id: 0, defender.id: 0}  # TODO: сохранять/загружать flee_attempts сейчас костыль, а еще лучше сделать фиксированные шанс, которые зависит от твоей ловкости и ловкости врага
    return battle
