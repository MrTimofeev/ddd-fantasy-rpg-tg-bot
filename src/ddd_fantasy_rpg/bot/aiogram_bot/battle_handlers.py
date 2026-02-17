from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from ddd_fantasy_rpg.domain.battle import BattleAction, BattleActionType, CombatantType
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
        
        # === Определяем combatan'ов ===
        player_combatant = None
        opponent_combatant = None
        
        for c in [battle._attacker, battle._defender]:
            if c.id == player_id:
                player_combatant = c
            else:
                opponent_combatant = c
        
        if not player_combatant or not opponent_combatant:
            await callback.message.answer("Ошибка: боевой участник не найден!")
            
        is_pvp = (opponent_combatant.combatant_type == CombatantType.PLAYER)
        
        
        
        # Создаем действие
        action = BattleAction(
            action_type=BattleActionType(action_type),
            skill_name=None,
            item_id=None
        )
        
        
        try:
            # === 1. Игрок делает ход === 
            result = battle.perform_action(player_id, action)
            response = _format_battle_result(result, battle, is_pvp)
            
            # === 2. Проверяем закончился ли бой после хода игрока ===
            if battle.is_finished:
                
                complete_battle_uc = use_cases['complete_battle']
                battle_outcome = await complete_battle_uc.execute(battle)
                
                await callback.bot.send_message(battle._attacker.id, response)
                if battle._defender.combatant_type != CombatantType.MONSTER:
                    await callback.bot.send_message(battle._defender.id, response)
                
                if battle_outcome["winner"] == "player":
                    result = "🏆 Победа! Добыча получена."
                    await callback.bot.send_message(battle._attacker.id, result)
                    result2 = "💀 Ты пал в бою.. Весь инвентарь потерян!"
                    if battle._defender.combatant_type != CombatantType.MONSTER:
                        await callback.bot.send_message(battle._defender.id, result2)
                    
                    
                await battle_repo.save(battle) # Сохраняем финальное состояние боя
                return
            
            if not is_pvp:  
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
            
            if is_pvp and not battle.is_finished:
                try:
                     # Форматируем действие противника
                    action_msg = _format_opponent_action(action, result)
                    
                    opponent_msg = (
                        f"⚔️ Твой противник сделал ход!\n"
                        f"{action_msg}\n\n"
                        f"❤️ Твоё HP: {battle._defender.current_hp}\n"
                        f"Твоя очередь атаковать!"
                    )
                    await callback.bot.send_message(
                        chat_id=int(opponent_combatant.id),
                        text=opponent_msg,
                        reply_markup=get_battle_keyboard(opponent_combatant.id)
                    )
                except Exception as e:
                    print(f'Ошибка отправки PVP-уведомления игроку {opponent_combatant.id}: {e}')
                    
            if battle.is_finished:
                
                compplete_battle_uc = use_cases['complete_battle']
                battle_outcome = await compplete_battle_uc.execute(battle)
                
                await callback.bot.send_message(battle._attacker.id, response)
                if battle._defender.combatant_type != CombatantType.MONSTER:
                    await callback.bot.send_message(battle._defender.id, response)
                
                if battle_outcome["winner"] == "player":
                    result = "🏆 Победа! Добыча получена."
                    await callback.bot.send_message(battle._attacker.id, result)
                    result2 = "💀 Ты пал в бою.. Весь инвентарь потерян!"
                    if battle._defender.combatant_type != CombatantType.MONSTER:
                        await callback.bot.send_message(battle._defender.id, result2)
                    
                    
                await battle_repo.save(battle) # Сохраняем финальное состояние боя
                return
            
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
    
def _format_battle_result(result: dict, battle, is_pvp: bool = False) -> str:
    # Определяем, кто игрок в этом контексте
    player_hp = None
    opponent_hp = None
    for c in [battle._attacker, battle._defender]:
        if hasattr(c, '_is_player_temp'):  # мы не храним это, поэтому определим по типу
            pass
    
    # Простой способ: предположим, что вызывающий знает свой HP
    # Но лучше переписать Battle, чтобы можно было получить HP по ID
    attacker_hp = battle._attacker.current_hp
    defender_hp = battle._defender.current_hp
    
    msg = f"❤️ Твоё HP: {attacker_hp if battle._attacker.id == battle._current_turn_owner_id else defender_hp}\n"
    opponent_label = "Игрока" if is_pvp else "Монстра"
    msg += f"👹 HP {opponent_label.lower()}: {defender_hp if battle._attacker.id == battle._current_turn_owner_id else attacker_hp}\n\n"
    
    if result["success"]:
        if result["action"] == "attack":
            target = "противника" if is_pvp else "монстра"
            msg += f"💥 Нанесено {result.get('damage', 0)} урона {target}!"
        elif result["action"] == "flee":
            msg += "🏃 Ты сбежал!"
        elif result['action'] == "use_item":
            msg += f"🧪 Использован предмет: +{result.get('heal', 0)} HP"
    else:
        msg += f"❌ {result['details']}"
    
    return msg

def _format_opponent_action(action: BattleAction, result: dict) -> str:
    """Форматирует действие противника для уведомления."""
    if not result["success"]:
        return f"❌ Противник попытался {action.action_type.value}, но неудачно."
    
    if action.action_type == BattleActionType.ATTACK:
        damage = result.get("damage", 0)
        return f"💥 Противник атаковал! Нанесено {damage} урона."
    elif action.action_type == BattleActionType.USE_SKILL:
        skill_name = result.get("details", "").split("Used ")[-1].split(" for")[0] if "Used " in result.get("details", "") else "скилл"
        if "damage" in result:
            damage = result["damage"]
            return f"🔥 Противник использовал {skill_name}! Нанесено {damage} урона."
        elif "heal" in result:
            heal = result["heal"]
            return f"💚 Противник использовал {skill_name}! Восстановлено {heal} HP."
        else:
            return f"✨ Противник использовал {skill_name}."
    elif action.action_type == BattleActionType.FLEE:
        return "🏃 Противник пытается сбежать!"
    elif action.action_type == BattleActionType.USE_ITEM:
        return "🧪 Противник использовал предмет."
    else:
        return f"🎲 Противник выполнил действие: {action.action_type.value}."