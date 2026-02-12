from ddd_fantasy_rpg.domain import Item, ItemType, ItemStats


def test_item_creation():
    item = Item(
        id="sword_1",
        name="Iron Sword",
        item_type=ItemType.WEAPON,
        level_required=3,
        rarity=2,
        stats=ItemStats(damage=10, strength=2)
    )
    assert item.name == "Iron Sword"
    assert item.stats.damage == 10


def test_invalid_rarity():
    try:
        Item(
            id="x",
            name="Bad",
            item_type=ItemType.WEAPON,
            level_required=1,
            rarity=6)  # rarity=6
        assert False
    except ValueError:
        pass
