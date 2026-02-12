from datetime import datetime

from ddd_fantasy_rpg.domain import Player, Race, PlayerClass, ExpeditionDistance, MonsterEncounter
from ddd_fantasy_rpg.infrastructure.repositories import (
    InMemoryPlayerRepository,
    InMemoryExpeditionRepository,
    InMemoryBattleRepository,
)
from ddd_fantasy_rpg.application import (
    StartExpeditionUseCase,
    CompleteExpeditionUseCase,
    StartBattleUseCase,
)

def main():
    # Репозитории
    player_repo = InMemoryPlayerRepository()
    exp_repo = InMemoryExpeditionRepository()
    battle_repo = InMemoryBattleRepository()
    
    # Игрок
    hero = Player("hero1", 1001, "Conan", Race.HUMAN, PlayerClass.WARRIOR)
    player_repo.save(hero)
    
    # Use Cases
    start_exp = StartExpeditionUseCase(player_repo, exp_repo)
    start_battle = StartBattleUseCase(player_repo, battle_repo)
    complete_exp = CompleteExpeditionUseCase(exp_repo, player_repo, start_battle)
    
    print("Начало вылазки...")
    start_exp.execute("hero1", ExpeditionDistance.FAR)
    
    # Симулируем завершение вылазки
    from ddd_fantasy_rpg.domain.expedition import Expedition
    exp = exp_repo.get_by_player_id("hero1")
    if exp is None:
        print("❌ Экспедиция не найдена!")
        return
    exp.end_time = datetime.now() # принудительно завершаем
    
    print("Найдено существо!")
    event = complete_exp.execute('hero1')
    if not isinstance(event, MonsterEncounter):
        print("⚠️ Непредвиденный тип события:", type(event))
        return
    
    print(f"Встреча: {event.monster.name} (Уровень {event.monster.level})")
    
    battle = battle_repo.get_active_battle_for_player('hero1')
    if battle is None:
        print("❌ Битва не была создана.!")
        return
    print(f"\n Бой начался! Ваше HP: {battle._attacker.current_hp}. HP монстра: {battle._defender.current_hp}")
    
    while not battle.is_finished:
        action = input("\nВыберите действие (attack / flee): ").strip().lower()
        from ddd_fantasy_rpg.domain.battle import BattleAction, BattleActionType
        if action == "attack":
            result = battle.perform_action('hero1', BattleAction(BattleActionType.ATTACK))
            print(f"Вы нанесли {result.get('damage', 0)} урона! HP монстра {battle._defender.current_hp}")
            if battle.is_finished:
                print("Ты победил!")
                print(f"Получен предмет: {event.monster.drop_items[0].name}")
                break
            
            monster_result = battle.perform_action(battle._defender.id, BattleAction(BattleActionType.ATTACK))
            print(f"Монстр нанес вам урон {monster_result.get('damage', 0)}. HP ваше хп {battle._attacker.current_hp}")
            
            if battle.is_finished:
                print("Ты прогирал")
                break
        
        elif action == "flee":
            result = battle.perform_action("hero1", BattleAction(BattleActionType.FLEE))
            if result["success"]:
                print("Ты сбежал!")
                break
            else:
                print("Побег не удался")
                monster_result = battle.perform_action(battle._defender.id, BattleAction(BattleActionType.ATTACK))
                print(f"Монстр нанес вам урон {monster_result.get('damage', 0)}")
    
    print("Игра закончена.")

if __name__ == "__main__":
    main()