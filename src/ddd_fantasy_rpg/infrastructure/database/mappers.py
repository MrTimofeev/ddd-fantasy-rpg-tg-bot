from typing import Optional, Dict, Any
from datetime import timezone

from ddd_fantasy_rpg.domain.player.player import Player
from ddd_fantasy_rpg.domain.player.race import Race
from ddd_fantasy_rpg.domain.player.player_profession import PlayerClass
from ddd_fantasy_rpg.domain.player.character_stats import CharacterStats
from ddd_fantasy_rpg.domain.player.inventory import Inventory
from ddd_fantasy_rpg.domain.player.equipment import Equipment
from ddd_fantasy_rpg.domain.expedition.expedition import Expedition
from ddd_fantasy_rpg.domain.expedition.expedition_distance import ExpeditionDistance
from ddd_fantasy_rpg.domain.expedition.expedition_event import PlayerDuelEncounter, MonsterEncounter
from ddd_fantasy_rpg.domain.expedition.expedition_status import ExpeditionStatus
from ddd_fantasy_rpg.domain.items.item_instance import ItemInstance
from ddd_fantasy_rpg.domain.items.item_type import ItemType
from ddd_fantasy_rpg.domain.items.item_stats import ItemStats
from ddd_fantasy_rpg.domain.battle.battle import Battle
from ddd_fantasy_rpg.domain.battle.combatant import Combatant, CombatantType
from ddd_fantasy_rpg.domain.monster.monster import Monster
from ddd_fantasy_rpg.infrastructure.database.models import PlayerORM, ExpeditionORM, BattleORM, PlayerItemORM, PlayerStatsORM

# === Вспомогательные функции для Item ===
def _item_to_dict(item: ItemInstance) -> Dict[str, Any]:
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


def _item_from_dict(data: Dict[str, Any]) -> ItemInstance:
    return ItemInstance(
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
    orm_player = PlayerORM(
        id=player.id,
        telegram_id=player.telegram_id,
        name=player.name,
        race=player.race.value, # Сохраняем значение enum
        player_profession=player.profession.value,
        level=player.level,
        exp=player.exp
    )

    
    stats = player.get_base_stats()
    orm_stats = PlayerStatsORM(
        player_id=player.id,
        strength=stats.strength,
        agility=stats.agility,
        intelligence=stats.intelligence,
        max_hp=stats.max_hp,
        damage=stats.damage,
        armor=stats.armor
    )
    orm_player.stats = orm_stats
    
    for item in player.get_inventory_items():
        orm_item = PlayerItemORM(
            id=item.id,
            player_id=player.id,
            template_id=item.template_id,
            name=item.name,
            item_type=item.item_type.value,
            stats_json={
                "strength": item.stats.strength,
                "agility": item.stats.agility,
                "intelligence": item.stats.intelligence,
                "max_hp": item.stats.max_hp,
                "damage": item.stats.damage,
            }, 
            is_equipped=item.is_equipped,
            slot_name=item.slot,
            modifiers_json=item.modifiers
        )
        orm_player.items.append(orm_item)
    
    return orm_player


def player_from_orm(orm: PlayerORM) -> Player:
    # 1. Восстанавливаем статы
    base_stats = CharacterStats(
        strength=orm.stats.strength,
        agility=orm.stats.agility,
        intelligence=orm.stats.intelligence,
        max_hp=orm.stats.max_hp,
        damage=orm.stats.damage,
        armor=orm.stats.armor
    )
    
    
    player = Player.__new__(Player)
    player.id = orm.id
    player.telegram_id = orm.telegram_id
    player.name = orm.name
    player.race = Race(orm.race)
    player.profession = PlayerClass(orm.player_profession)
    player.level = orm.level
    player.exp = orm.exp
    player.base_stats = base_stats
    
    player._current_hp = base_stats.max_hp
    
    player._inventory = Inventory()
    player._equipment = Equipment()
    player._is_dead = False
    player._death_timestamp = None
    player._pending_events = []
    
    for orm_item in orm.items:
        item_stats = CharacterStats(**orm_item.stats_json)
        
        item = ItemInstance(
            id=orm_item.id,
            name=orm_item.name,
            template_id=orm_item.template_id,
            level_required=0, # Нужно сохранить в БД если важно
            item_type=ItemType(orm_item.item_type),
            stats=item_stats,
            owner_id=orm.id,
            modifiers=orm_item.modifiers_json or {}
        )
    
    
        if orm_item.is_equipped and orm_item.slot_name:
            # Восстанавливаем внутреннее состояние предмета
            item._is_equipped = True
            item._slot = orm_item.slot_name
            player._inventory.add_item(item)
            setattr(player._equipment, orm_item.slot_name, item)
        else:
            player._inventory.add_item(item)
            
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
        stats=CharacterStats(
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
