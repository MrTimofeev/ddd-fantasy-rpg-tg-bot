import asyncio
from aiogram import Bot

from ddd_fantasy_rpg.application.async_factories import create_async_use_cases
from ddd_fantasy_rpg.bot.aiogram_bot.keyboards import get_battle_keyboard


async def check_completed_expeditions(bot: Bot, async_session_maker: callable):
    """
    Фоновая задача: каждые 30 сек проверяет, если ли завершенные вылазки.
    Если есть - генерирует событие и уведомляет игрока.
    """
    while True:
        try:
            async with async_session_maker() as session:
                use_cases = create_async_use_cases(session)
                exp_repo = use_cases["complete_expedition"]._expedition_repo

                expeditions = await exp_repo.get_all_active_expeditions()

                for exp in expeditions:
                    try:
                        # Завершаем вылазку -> генерируем событие
                        event = await use_cases["complete_expedition"].execute(
                            exp.player_id)

                        # Отправляем уведомления игроку
                        if hasattr(event, "monster"):
                            msg = (
                                f"🗺️ Твоя вылазка завершена!\n"
                                f"👹 Ты встретил {event.monster.name} (ур. {event.monster.level})!\n"
                                f"⚔️ Бой начинается!"
                            )
                            await bot.send_message(chat_id=int(exp.player_id), text=msg, reply_markup=get_battle_keyboard(exp.player_id))
                            
                        # TODO: для торговца, ресурсов - другие сообщения
                    except Exception as e:
                        print(f"Ошибка при обработке вылазки {exp.player_id}: {e}")
                        

        except Exception as e:
            print(f'Ошибка в фоновой задаче: {e}')

        await asyncio.sleep(30)
