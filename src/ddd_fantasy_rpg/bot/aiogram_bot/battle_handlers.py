from aiogram import Router, F
from aiogram.types import CallbackQuery

from ddd_fantasy_rpg.domain.battle import BattleAction, BattleActionType, CombatantType
from ddd_fantasy_rpg.infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from ddd_fantasy_rpg.bot.aiogram_bot.keyboards import get_battle_keyboard
from ddd_fantasy_rpg.application.async_factories import create_async_use_cases

router = Router()


@router.callback_query(F.data.startswith("battle_"))
async def handle_battle_action(callback: CallbackQuery, async_session_maker):
    _, player_id, action_type = callback.data.split("_", 2)

    if str(callback.from_user.id) != player_id:
        await callback.answer("Это не твой бой!", show_alert=True)
        return
    try:
        use_cases = create_async_use_cases()

        async with SqlAlchemyUnitOfWork(async_session_maker) as uow:
            action = BattleAction(action_type=BattleActionType(action_type))
            result = await use_cases["perform_battle_action"].execute(player_id, action, uow)

            if result.is_finished:
                # Отправляем финальное сообщение игроку
                await callback.message.answer(result.message)

                # Дополнительные сообщения о победе/поражении
                if result.battle_outcome and result.battle_outcome.get("winner") == "player":
                    await callback.bot.send_message(player_id, "🏆 Победа! Добыча получена.")
                    if result.opponent_id[1] == CombatantType.PLAYER:
                        await callback.bot.send_message(result.opponent_id[0], "💀 Ты пал в бою... Весь инвентарь потерян!")
                elif result.battle_outcome and result.battle_outcome.get("player_died"):
                    await callback.bot.send_message(player_id, "💀 Ты пал в бою... Весь инвентарь потерян!")
                    if result.opponent_id[1] == CombatantType.PLAYER:
                        await callback.bot.send_message(result.opponent_id[0], "🏆 Победа! Добыча получена.")
            else:
                # Обновляем интерфейс
                await callback.bot.send_message(
                    player_id,
                    result.message,
                    reply_markup=get_battle_keyboard(player_id)
                )

                # Для PVP отправляем уведомление противнику
                if result.requires_opponent_notification and result.opponent_id:
                    opponent_msg = (
                        f"⚔️ Твой противник сделал ход!\n"
                        f"❤️ Твоё HP: {result.message.split('HP игрока: ')[1].split()[0]}\n"
                        f"Твоя очередь атаковать!"
                    )
                    try:
                        await callback.bot.send_message(
                            chat_id=int(result.opponent_id[0]),
                            text=opponent_msg,
                            reply_markup=get_battle_keyboard(
                                result.opponent_id[0])
                        )
                    except Exception as e:
                        print(f"Ошибка оправки PVP-уведомления: {e}")

    except ValueError as e:
        await callback.answer(str(e), show_alert=True)
    except Exception as e:
        await callback.answer(f"Ошибка: {e}", show_alert=True)

    await callback.answer()
