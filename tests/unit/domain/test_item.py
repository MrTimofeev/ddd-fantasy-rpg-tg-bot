from ddd_fantasy_rpg.domain import Item, ItemType, ItemStats, Rarity


def test_item_creation():
    item = Item(
        id="sword_1",
        name="Iron Sword",
        item_type=ItemType.WEAPON,
        level_required=3,
        rarity=Rarity.UNCOMMON,
        stats=ItemStats(damage=10, strength=2)
    )
    assert item.name == "Iron Sword"
    assert item.stats.damage == 10
