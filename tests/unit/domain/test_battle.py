from ddd_fantasy_rpg.domain.battle import (
    Battle, Combatant, CombatantStats, CombatantType, BattleAction, BattleActionType
)

from ddd_fantasy_rpg.domain.skills.skill import Skill, SkillType


def test_battle_attack_and_kill():
    hero = Combatant(
        id="hero1",
        name="Hero",
        combatant_type=CombatantType.PLAYER,
        stats=CombatantStats(strength=20, agility=8,
                             intelligence=5, max_hp=50),
        current_hp=50
    )
    goblin = Combatant(
        id="gob1",
        name="Goblin",
        combatant_type=CombatantType.MONSTER,
        stats=CombatantStats(strength=5, agility=6, intelligence=2, max_hp=20),
        current_hp=20
    )

    battle = Battle(hero, goblin)

    while not battle.is_finished:
        current_turn = battle._current_turn_owner_id
        if current_turn == "hero1":
            battle.perform_action(
                "hero1", BattleAction(BattleActionType.ATTACK))
        elif current_turn == "gob1":
            battle.perform_action(
                "gob1", BattleAction(BattleActionType.ATTACK))
        else:
            raise AssertionError("Unknown combatant turn")

    # Проверка результата
    assert battle.winner is not None
    assert battle.winner.id == "hero1"


def test_flee_success():
    weak = Combatant("weak", "Weak", CombatantType.PLAYER,
                     CombatantStats(1, 20, 1, 10), 10)
    strong = Combatant("strong", "Strong", CombatantType.MONSTER,
                       CombatantStats(20, 1, 1, 100), 100)

    battle = Battle(weak, strong)
    # Слабый пытается сбежать — должен succeed с высоким шансом
    result = battle.perform_action("weak", BattleAction(BattleActionType.FLEE))
    assert result["success"] is True
    assert battle.is_finished
    assert battle.winner is not None
    assert battle.winner.id == "strong"  # потому что слабый сбежал
    
def test_use_heal_skill():
    hero = Combatant(
        id="hero",
        name="Cleric",
        combatant_type=CombatantType.PLAYER,
        stats=CombatantStats(strength=5, agility=6, intelligence=12, max_hp=60),
        current_hp=30,
        skills=[Skill("Heal", SkillType.HEAL, base_power=20, cooldown_turns=2)]
    )
    dummy = Combatant(
        id="dummy", name="Dummy", combatant_type=CombatantType.MONSTER,
        stats=CombatantStats(1,1,1,10), current_hp=10
    )

    battle = Battle(hero, dummy)

    # Используем скилл
    action = BattleAction(BattleActionType.USE_SKILL, skill_name="Heal")
    result = battle.perform_action("hero", action)

    assert result["success"] is True
    assert "healed for" in result["details"]
    assert hero.current_hp == 60

    # Попытка использовать снова — должна быть ошибка
    result2 = battle.perform_action("dummy", BattleAction(BattleActionType.ATTACK))  # ход монстра
    result3 = battle.perform_action("hero", action)  # снова герой
    assert result3["success"] is False
    assert "colldown" in result3["details"]
    