from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from ddd_fantasy_rpg.domain.battle import BattleAction, BattleActionType
from ddd_fantasy_rpg.bot.aiogram_bot.keyboards import get_battle_keyboard

router = Router()


@router.callback_query(F.data.startswith("battle_"))
async def handle_battle_action(callback: CallbackQuery, async_session_maker):
    _, player_id, action_type = callback.data.split("_", 2)
    
    if str(callback.from_user.id) != player_id:
        await callback.answer("Это не твой бой!", show_alert=True)
        return
    
    async with async_session_maker() as session:
        from ddd_fantasy_rpg.application.async_factories import create_async_use_cases
        use_cases = create_async_use_cases(session)
        battle_repo = use_cases["start_battle"]._battle_repo
        
        battle = await battle_repo.get_active_battle_for_player(player_id)
        if not battle:
            await callback.message.answer("Бой уже завершен!")
            return
        
        # Создаем действие
        action = BattleAction(
            action_type=BattleActionType(action_type),
            skill_name=None,
            item_id=None
        )
        
        
        try:
            # === 1. Игрок делает ход === 
            result = battle.perform_action(player_id, action)
            response = _format_battle_result(result, battle)
            
            # === 2. Проверяем закончился ли бой после хода игрока ===
            if battle.is_finished:
                
                compplete_battle_uc = use_cases['complete_battle']
                battle_outcome = await compplete_battle_uc.execute(battle)
                
                if battle_outcome["winner"] == "player":
                    response += "\n\n 🏆 Победа! Добыча получена."
                else:
                    response += "\n\n 💀 Ты пал в бою.. Весь инвентарь потерян!"
                    
                await callback.message.answer(response)
                await battle_repo.save(battle) # Сохраняем финальное состояние боя
                return
                
            # === 4. Проверяем, завершился ли бой после хода монстра === 
            opponent_id = battle._defender.id if battle._attacker.id == player_id else battle._attacker.id
            monster_action = BattleAction(action_type=BattleActionType.ATTACK)
            monster_result = battle.perform_action(opponent_id, monster_action)
            response += f"\n\n 👹 Монстр атакует!\n{monster_result.get('damage', 0)} урона."
            
            if battle.is_finished:
                compplete_battle_uc = use_cases["complete_battle"]
                battle_outcome = await compplete_battle_uc.execute(battle)
                
                if battle_outcome["winner"] == "player":
                    response += "\n\n 🏆 Невероятно! Ты выжил и победил!"
                else:
                    response += "\n\n 💀 Ты пал в бою..."
                    
                await callback.message.answer(response)
                await battle_repo.save(battle)
                return
            
            # сохраняем бой после действий
            await battle_repo.save(battle)
            
            # === 5. Обновляем интрефейс, если бой продолжается ===
            try:
                await callback.message.answer(
                    response,
                    reply_markup=get_battle_keyboard(player_id)
                )
            except TelegramBadRequest:
                pass # Игнорируем, если сообщение не изменилось
        
        except ValueError as e:
            await callback.answer(str(e), show_alert=True)
        except Exception as e:
            await callback.answer(f"Ошибка: {e}", show_alert=True)
            
    await callback.answer()
    
def _format_battle_result(result: dict, battle) -> str:
    msg = f"❤️ Твоё HP: {battle._attacker.current_hp}\n"
    msg += f"👹 HP монстра: {battle._defender.current_hp}\n\n"
    
    if result["success"]:
        if result["action"] == "attack":
            msg +=f"💥 Нанесено {result.get('damage', 0)} урона!"
        elif result["action"] == "flee":
            msg += "🏃 Ты сбежал!"
        elif result['action'] == "use_item":
            msg += f"🧪 Использован предмет: +{result.get('heal', 0)} HP"
    else:
        msg += f"❌ {result['details']}"
    
    return msg