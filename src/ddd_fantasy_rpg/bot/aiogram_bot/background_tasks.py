import asyncio
from aiogram import Bot
from collections import defaultdict

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
                        print(
                            f"Ошибка при обработке вылазки {exp.player_id}: {e}")

        except Exception as e:
            print(f'Ошибка в фоновой задаче: {e}')

        await asyncio.sleep(30)


async def match_active_expeditions_for_pvp(bot: Bot, async_session_maker: callable):
    """фоновая задача: которая каждый 10 сек ищект пары для PVP"""
    while True:
        try:
            async with async_session_maker() as session:
                use_cases = create_async_use_cases(session)
                exp_repo = use_cases["exp_repo"]
                player_repo = use_cases["player_repo"]
                start_battle_uc = use_cases["start_battle"]

                # 1. Получаем все активные вылазки
                active_expeditions = await exp_repo.get_active_expeditions()
                if not active_expeditions:
                    await asyncio.sleep(10)
                    continue

                # 2. Загружаем игроков
                player_ids = [e.player_id for e in active_expeditions]
                player_tasks = [player_repo.get_by_id(
                    pid) for pid in player_ids]
                players = await asyncio.gather(*player_tasks, return_exceptions=True)

                # Фильтруем успешные вылазки
                player_map = {}
                for pid, p in zip(player_ids, players):
                    if isinstance(p, Exception):
                        print(f"Ошибка загрузки игрока {pid}: {p}")
                    elif p is None:
                        print(f"Игрок {pid} на найден")
                    else:
                        player_map[pid] = p

                # 3. Связываем вылазки с игроками
                valid_pairs = []
                for exp in active_expeditions:
                    if exp.player_id in player_map:
                        valid_pairs.append((exp, player_map[exp.player_id]))
                    else:
                        print(
                            f"Пропускаем вылазку {exp.player_id}: игрок не найден")

                if len(valid_pairs) < 2:
                    await asyncio.sleep(10)
                    continue

                # 4. Групируем по distance
                by_distance = defaultdict(list)
                for exp, player in valid_pairs:
                    by_distance[exp.distance].append((exp, player))

                # 5. Матчим пары
                mathed_player_ids = set()
                for distance, pairs in by_distance.items():
                    # Сортируем по уровню

                    pairs.sort(key=lambda x: x[1].level)

                    i = 0
                    while i < len(pairs) - 1:
                        exp1, p1 = pairs[i]
                        exp2, p2 = pairs[i + 1]

                        # Пропускаем если кто-то уже в паре
                        if p1.id in mathed_player_ids or p2.id in mathed_player_ids:
                            i += 1
                            continue

                        # проверяем баланс (разница <= 2 уровня)
                        if abs(p1.level - p2.level) <= 2:
                            try:
                                # Прерываем вылазки
                                exp1.interrupt_for_duel(p2.id)
                                exp2.interrupt_for_duel(p1.id)

                                # Сохраняем
                                await exp_repo.save(exp1)
                                await exp_repo.save(exp2)

                                # Запускаем бой
                                await start_battle_uc.execute(p1.id, p2.id)

                                # Отмечаем как сматченных
                                mathed_player_ids.update([p1.id, p2.id])

                                # Уведомляем игроков
                                msg1 = (
                                    f"⚔️ Во время вылазки ты встретил игрока {p2._name}!\n"
                                    f"Бой начинается!"
                                )
                                msg2 = (
                                    f"⚔️ Во время вылазки ты встретил игрока {p1._name}!\n"
                                    f"Бой начинается!"
                                )

                                try:
                                    await bot.send_message(chat_id=int(p1.id), text=msg1, reply_markup=get_battle_keyboard(p1.id))
                                    await bot.send_message(chat_id=int(p2.id), text=msg2)
                                except Exception as e:
                                    print(f"Ошибка отправки уведомления: {e}")

                                print(f"Создана PVP дуэль: {p1.id} VS {p2.id}")

                                i += 2
                            except Exception as e:
                                print(
                                    f"Ошибка созадания дуэли {p1.id} VS {p2.id}: {e}")
                                i += 1
                        else:
                            i += 1

        except Exception as e:
            print(f'Ошибка матчинка PVP: {e}')

        await asyncio.sleep(10)
