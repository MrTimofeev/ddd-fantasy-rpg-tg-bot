import asyncio
from aiogram import Bot

from ddd_fantasy_rpg.application.async_factories import create_async_use_cases
from ddd_fantasy_rpg.bot.aiogram_bot.keyboards import get_battle_keyboard
from ddd_fantasy_rpg.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


async def check_completed_expeditions(bot: Bot, async_session_maker: callable):
    """
    Фоновая задача: каждые 30 сек проверяет, если ли завершенные вылазки.
    Если есть - генерирует событие и уведомляет игрока.
    """
    while True:
        try:
            async with async_session_maker() as session:
                use_cases = create_async_use_cases()

                async with SqlAlchemyUnitOfWork(async_session_maker) as uow:
                    expeditions = await use_cases["get_active_expeditions"].execute(uow)

                    for exp in expeditions:
                        try:
                            # Завершаем вылазку -> генерируем событие
                            event = await use_cases["complete_expedition"].execute(
                                exp.player_id,
                                uow
                            )

                            # Отправляем уведомления игроку
                            # TODO: вынести в отдельную функцию уведомления
                            if hasattr(event, "monster"):
                                msg = (
                                    f"🗺️ Твоя вылазка завершена!\n"
                                    f"👹 Ты встретил {event.monster.name} (ур. {event.monster.level})!\n"
                                    f"⚔️ Бой начинается!"
                                )
                                await bot.send_message(chat_id=int(exp.player_id), text=msg, reply_markup=get_battle_keyboard(exp.player_id))

                            # TODO: для торговца, ресурсов - другие сообщения
                        except Exception as e:
                            print(
                                f"Ошибка при обработке вылазки {exp.player_id}: {e}")

        except Exception as e:
            print(f'Ошибка в фоновой задаче: {e}')

        await asyncio.sleep(30)


async def match_active_expeditions_for_pvp(bot: Bot, async_session_maker: callable):
    """фоновая задача: которая каждый 10 сек ищект пары для PVP"""
    while True:
        try:
            use_cases = create_async_use_cases()

            async with SqlAlchemyUnitOfWork(async_session_maker) as uow:
                matches = await use_cases["match_pvp_expeditions"].execute(uow)
                # Отправляем уведомления
                # TODO: Сделать отдельный модуль для оправки уведомлений
                for match in matches:
                    try:
                        msg1 = (
                            f"⚔️ Во время вылазки ты встретил игрока {match.player2_name}!\n"
                            f"Бой начинается!"
                        )
                        msg2 = (
                            f"⚔️ Во время вылазки ты встретил игрока {match.player1_name}!\n"
                            f"Бой начинается!"
                        )
                        await bot.send_message(chat_id=int(match.player1_id), text=msg1, reply_markup=get_battle_keyboard(match.player1_id))
                        await bot.send_message(chat_id=int(match.player2_id), text=msg1)
                        print(
                            f"Создана PVP дуэль: {match.player1_id} VS {match.player2_id}")
                    except Exception as e:
                        print(f"Ошибка отправки удедомления: {e}")

        except Exception as e:
            print(f'Ошибка матчинка PVP: {e}')

        await asyncio.sleep(10)
