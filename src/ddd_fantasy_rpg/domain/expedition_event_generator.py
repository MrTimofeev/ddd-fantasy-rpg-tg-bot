import random

from .expedition import (
    ExpeditionDistance,
    MonsterEncounter,
    TraderEncounter,
    ResourceGathering,
    PlayerDuelEncounter,
)

from .monster import Monster
from .item import Item, ItemType, ItemStats, Rarity
from .random_provider import RandomProvider


def generate_monster_for_distance(
    distance: ExpeditionDistance,
    random_provider: RandomProvider
) -> Monster:
    """Геренируем монстра в зависимости от дальности вылазки."""
    level_map = {
        ExpeditionDistance.NEAR: (1, 3),
        ExpeditionDistance.MEDIUM: (3, 6),
        ExpeditionDistance.FAR: (6, 10),
    }
    min_lvl, max_lvl = level_map[distance]
    level = random_provider.randint(min_lvl, max_lvl)

    # Простая таблица монстров
    monster = [
        ("Goblin", 5, 50),
        ("Orc", 10, 100),
        ("Troll", 15, 150),
        ("Dragon", 20, 200),
    ]

    name, base_dmg, max_hp = random_provider.choice(monster[:level // 2 + 1])

    # Дроп - случайный пердмет
    rarity = Rarity.from_level(level)
    drop_item = Item(
        id=f"drop_{name.lower()}_{level}",
        name=f"{name}'s Loot",
        item_type=ItemType.WEAPON,
        level_required=level,
        rarity=rarity,
        stats=ItemStats(damage=level * 2, strength=level // 2),
    )

    return Monster(
        id=f"mob_{random.randint(1000, 9999)}",
        name=name,
        level=level,
        base_damage=base_dmg,
        max_hp=max_hp,
        drop_items=[drop_item],
        flee_difficulty=min(80, 20 + level * 5),
    )


def generate_event_for_expedition(
    distance: ExpeditionDistance,
    random_provider: RandomProvider
) -> MonsterEncounter:
    """
    Для MVP всегда генерируем монстра.
    Позже можно добавить веса: 70% монстр, 20% торговец, 10% ресурсы.
    """

    monster = generate_monster_for_distance(distance, random_provider)
    return MonsterEncounter(monster=monster)
