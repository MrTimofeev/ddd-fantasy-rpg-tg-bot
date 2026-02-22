import asyncio
from aiogram import Bot

from ddd_fantasy_rpg.application.use_cases.complete_expedition import CompleteExpeditionUseCase
from ddd_fantasy_rpg.application.use_cases.get_active_expeditions import GetActiveExpeditionUseCase
from ddd_fantasy_rpg.application.use_cases.match_pvp_expeditions import MatchPvpExpeditionsUseCase
from ddd_fantasy_rpg.infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from ddd_fantasy_rpg.domain.notifications import NotificationService
from ddd_fantasy_rpg.domain.expedition import MonsterEncounter
from ddd_fantasy_rpg.domain.exceptions import ExpeditionNotFinishedError


class ExpeditionCompletionBackgroundTask:
    """
    Фоновая задача: каждые 30 сек проверяет, если ли завершенные вылазки.
    Если есть - генерирует событие и уведомляет игрока.
    """

    def __init__(
        self,
        complete_expetidion_use_case: CompleteExpeditionUseCase,
        get_active_expedition_use_case: GetActiveExpeditionUseCase,
        notification_service: NotificationService,
        async_session_maker: callable
    ):
        self._complete_expedition_uc = complete_expetidion_use_case
        self._get_acive_expedition_uc = get_active_expedition_use_case
        self._notification_service = notification_service
        self._session_maker = async_session_maker

    async def run(self):
        while True:
            try:

                async with SqlAlchemyUnitOfWork(self._session_maker) as uow:
                    expeditions = await self._get_acive_expedition_uc.execute(uow)

                    for exp in expeditions:
                        try:
                            # Завершаем вылазку -> генерируем событие
                            event = await self._complete_expedition_uc.execute(exp.player_id, uow)

                            # Отправляем уведомления игроку
                            if isinstance(event, MonsterEncounter):
                                await self._notification_service.notify_expedition_complete(
                                    player_id=exp.player_id,
                                    monster_name=event.monster.name,
                                    monster_level=event.monster.level,
                                )

                            # TODO: для торговца, ресурсов - другие сообщения
                        except ExpeditionNotFinishedError:
                            continue
                        except Exception as e:
                            print(
                                f"Ошибка при обработке вылазки {exp.player_id}: {e}")
            except Exception as e:
                print(f'Ошибка в фоновой задаче: {e}')

            await asyncio.sleep(30)


class PvpMatchingBackgroundTask:
    """Фоновая задача для матчинга PvP дуэлей"""

    def __init__(
        self,
        match_pvp_expedition_use_case: MatchPvpExpeditionsUseCase,
        notification_service: NotificationService,
        async_session_maker: callable
    ):
        self._match_pvp_expedition_uc = match_pvp_expedition_use_case
        self._notification_service = notification_service
        self._session_maker = async_session_maker

    async def run(self):
        """фоновая задача: которая каждый 10 сек ищект пары для PVP"""
        while True:
            try:
                async with SqlAlchemyUnitOfWork(self._session_maker) as uow:
                    matches = await self._match_pvp_expedition_uc.execute(uow)

                    # Отправляем уведомления
                    if matches:
                        await self._notification_service.notify_pvp_match_found(matches)

            except Exception as e:
                print(f'Ошибка матчинка PVP: {e}')

            await asyncio.sleep(10)
