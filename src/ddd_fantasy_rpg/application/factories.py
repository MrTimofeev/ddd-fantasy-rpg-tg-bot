from ddd_fantasy_rpg.domain.player.stats_calculation_service import StatsCalculationService
from ddd_fantasy_rpg.domain.expedition.expedition_factory import ExpeditionFactory
from ddd_fantasy_rpg.domain.expedition.expedition_event_generator import ExpeditionEventGenerator
from ddd_fantasy_rpg.infrastructure.time import UtcTimeProvider
from ddd_fantasy_rpg.infrastructure.random import SystemRandomProvider
from ddd_fantasy_rpg.infrastructure.notifications import TelegramNotificationService
from ddd_fantasy_rpg.infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from ddd_fantasy_rpg.bot.aiogram_bot.dependency_context import DependencyContext
from ddd_fantasy_rpg.application.events.dispatcher import EventDispatcher
from ddd_fantasy_rpg.application.formatters.battle_formatter import BattleMessageFormatter
from ddd_fantasy_rpg.application.events.handlers.telegram_notifier import PlayerCreatedTelegramHandler, ExpeditionCreatedTelegramHandler
from ddd_fantasy_rpg.application import (
    StartExpeditionUseCase,
    StartBattleUseCase,
    CompleteBattleUseCase,
    GetActiveExpeditionUseCase,
    MatchPvpExpeditionsUseCase,
    PerformBattleActionUseCase,
    CreatePlayerUseCase,
    GenerateEventUseCase,
    CompleteExpeditionByTimeUseCase,
    ProcessCompletedExpeditionUseCase,
    GetCompletedExpeditionUseCase,
)


class ApplicationFactory:
    """Фабрика для создания всех зависимостей приложения."""

    def __init__(
        self,
        bot: "Bot",
        async_session_maker,
    ):
        self.bot = bot
        self.session_maker = async_session_maker

        # инфраструктурные зависимости
        self.time_provider = UtcTimeProvider()
        self.random_provider = SystemRandomProvider()
        self.message_formatter = BattleMessageFormatter()
        self.notification_service = TelegramNotificationService(
            bot, self.message_formatter)
        self.unit_of_work = SqlAlchemyUnitOfWork(self.session_maker)
        self.dispatcher = EventDispatcher()
        
        self.stats_service = StatsCalculationService()
        self.event_generator = ExpeditionEventGenerator(self.random_provider)
        
        # === Создаем Use Case ===
        # === Generate Event ===
        self.generate_event_uc = GenerateEventUseCase(self.random_provider)
        self.expedition_factory = ExpeditionFactory(
            self.event_generator,
            self.time_provider,
        )

        # === Battle ===
        self.start_battle_uc = StartBattleUseCase(self.notification_service)
        self.start_exp_uc = StartExpeditionUseCase(
            self.expedition_factory,
            self.dispatcher,
            self.time_provider,
            self.unit_of_work,
        )
        self.complete_battle_uc = CompleteBattleUseCase()
        self.perform_battle_action_uc = PerformBattleActionUseCase(
            self.complete_battle_uc)
        self.match_pvp_uc = MatchPvpExpeditionsUseCase()

        # === Expedition ===
        self.complete_exp_by_time_uc = CompleteExpeditionByTimeUseCase(
            self.time_provider)
        self.process_comppleted_exp_uc = ProcessCompletedExpeditionUseCase(
            self.start_battle_uc, self.time_provider, self.random_provider)
        self.get_completed_exp_uc = GetCompletedExpeditionUseCase()
        self.get_active_exp_uc = GetActiveExpeditionUseCase()

        # === Player ===
        self.create_player_uc = CreatePlayerUseCase(self.unit_of_work, self.dispatcher, self.stats_service)


    def create_background_tasks(self):
        """Создает фоновые задачи"""
        from ddd_fantasy_rpg.bot.aiogram_bot.background_tasks import (
            ExpeditionCompletionBackgroundTask,
            PvpMatchingBackgroundTask,
            ExpeditoinEventProcessingBackgroundTask,
        )

        expedition_complete_task = ExpeditionCompletionBackgroundTask(
            complete_expetidion_by_time_use_case=self.complete_exp_by_time_uc,
            get_active_expedition_use_case=self.get_active_exp_uc,
            notification_service=self.notification_service,
            async_session_maker=self.session_maker
        )

        process_completed_expeditoin = ExpeditoinEventProcessingBackgroundTask(
            self.process_comppleted_exp_uc,
            self.get_completed_exp_uc,
            self.notification_service,
            self.session_maker,
        )

        pvp_task = PvpMatchingBackgroundTask(
            match_pvp_use_case=self.match_pvp_uc,
            notification_service=self.notification_service,
            async_session_maker=self.session_maker
        )

        return {
            "complete_expetidion_by_time": expedition_complete_task,
            "start_event_for_complete_expeditions": process_completed_expeditoin,
            "pvp_matching": pvp_task,
        }

    def create_dependency_context(self) -> DependencyContext:
        """Создает единый контект зависимостей."""

        return DependencyContext(
            # Use Cases
            create_player_use_case=self.create_player_uc,
            start_expedition_use_case=self.start_exp_uc,
            perform_battle_action_use_case=self.perform_battle_action_uc,

            # Services
            notification_service=self.notification_service,
            message_formatter=self.message_formatter,
        )
        
    def create_event_dispatcher(self) -> None:
        """Регистрирует хендлеры для обработки событий"""
        
        self.dispatcher.register(PlayerCreatedTelegramHandler(self.notification_service, self.unit_of_work))
        self.dispatcher.register(ExpeditionCreatedTelegramHandler(self.notification_service, self.unit_of_work))
