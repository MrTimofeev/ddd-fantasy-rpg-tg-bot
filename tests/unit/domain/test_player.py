from ddd_fantasy_rpg.domain.player import Player, Race, PlayerClass
from ddd_fantasy_rpg.domain.shared.item import Item, ItemType

def test_player_creation():
    player = Player(
        player_id="123",
        telegram_id=987654321,
        name="MrSoulKing",
        race=Race.HUMAN,
        player_profession=PlayerClass.WARRIOR
    )
    assert player.level == 1
    assert player.id == "123"
    assert "strength" in player.get_total_stats()
    
def test_equip_item_requires_level():
    player = Player("1", 123, "Lowbie", Race.HUMAN, PlayerClass.MAGE)
    high_level_item = Item(id="sword1", name="Excalibur", item_type= ItemType.WEAPON, level_required=10, rarity=5)
    
    try:
        player.equip_item(high_level_item, "weapon")
        assert False, "Shoulf have raised ValueError"
    except ValueError as e:
        assert "requires level 1" in str(e)
        
        
def test_add_item_to_inventory():
    player = Player('1', 123, "Looter", Race.ELF, PlayerClass.ROGUE)
    item = Item(id="dagger", name="Steel Dagger", item_type=ItemType.WEAPON, level_required=1, rarity=2)
    player.add_item(item)
    assert len(player.inventory) == 1
    assert player.inventory[0].name == "Steel Dagger"