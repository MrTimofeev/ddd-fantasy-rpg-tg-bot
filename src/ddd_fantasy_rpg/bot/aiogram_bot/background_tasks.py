import asyncio

from ddd_fantasy_rpg.application.use_cases.complete_expediton_by_time import CompleteExpeditionByTimeUseCase
from ddd_fantasy_rpg.application.use_cases.process_completed_expedition import ProcessCompletedExpeditionUseCase
from ddd_fantasy_rpg.application.use_cases.get_active_expeditions import GetActiveExpeditionUseCase
from ddd_fantasy_rpg.application.use_cases.get_completed_expedition import GetCompletedExpeditionUseCase
from ddd_fantasy_rpg.application.use_cases.match_pvp_expeditions import MatchPvpExpeditionsUseCase
from ddd_fantasy_rpg.infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from ddd_fantasy_rpg.domain.common.notifications import NotificationService


class ExpeditionCompletionBackgroundTask:
    """
    Фоновая задача: каждые 30 сек проверяет, если ли завершенные вылазки.
    запускает Use case для смены статуса экспедиции
    """

    def __init__(
        self,
        complete_expetidion_by_time_use_case: CompleteExpeditionByTimeUseCase,
        get_active_expedition_use_case: GetActiveExpeditionUseCase,
        notification_service: NotificationService,
        async_session_maker: callable
    ):
        self._complete_expedition_by_time_uc = complete_expetidion_by_time_use_case
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
                            # Завершаем вылазку
                            await self._complete_expedition_by_time_uc.execute(exp.player_id, uow)
                        except Exception as e:
                            print(
                                f"Ошибка при обработке вылазки {exp.player_id}: {e}")
            except Exception as e:
                print(f'Ошибка в фоновой задаче: {e}')

            await asyncio.sleep(30)


class ExpeditoinEventProcessingBackgroundTask:
    """
    Фоновая задача: каждые 30 сек, получает все завершенные вылазки и запускает их события.
    """

    def __init__(
        self,
        start_evetnt_for_complete_expedition: ProcessCompletedExpeditionUseCase,
        get_complete_expedition_use_case: GetCompletedExpeditionUseCase,
        notification_service: NotificationService,
        async_session_maker: callable,
    ):
        self._start_evet_for_complete_expedition = start_evetnt_for_complete_expedition
        self._get_complete_expedition_uc = get_complete_expedition_use_case
        self._notification_service = notification_service
        self._session_maker = async_session_maker

    async def run(self):
        while True:
            try:
                async with SqlAlchemyUnitOfWork(self._session_maker) as uow:
                    expeditions = await self._get_complete_expedition_uc.execute(uow)

                    for exp in expeditions:
                        try:
                            # запускаем событие
                            await self._start_evet_for_complete_expedition.execute(exp, uow)
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
        match_pvp_use_case: MatchPvpExpeditionsUseCase,
        notification_service: NotificationService,
        async_session_maker: callable
    ):
        self._match_pvp_expedition_uc = match_pvp_use_case
        self._notification_service = notification_service
        self._session_maker = async_session_maker

    async def run(self):
        """фоновая задача: которая каждый 10 сек ищект пары для PVP"""
        while True:
            try:
                async with SqlAlchemyUnitOfWork(self._session_maker) as uow:
                    await self._match_pvp_expedition_uc.execute(uow)

                    # Отправляем уведомления
                    # if matches:
                    #     await self._notification_service.notify_pvp_match_found(matches)

            except Exception as e:
                print(f'Ошибка матчинка PVP: {e}')

            await asyncio.sleep(10)
