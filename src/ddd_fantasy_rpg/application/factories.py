from ddd_fantasy_rpg.infrastructure.time import UtcTimeProvider
from ddd_fantasy_rpg.infrastructure.random import SystemRandomProvider
from ddd_fantasy_rpg.infrastructure.notifications import TelegramNotificationService
from ddd_fantasy_rpg.infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from ddd_fantasy_rpg.bot.aiogram_bot.dependency_context import DependencyContext
from ddd_fantasy_rpg.application import (
    StartExpeditionUseCase,
    StartBattleUseCase,
    CompleteExpeditionUseCase,
    CompleteBattleUseCase,
    GetActiveExpeditionUseCase,
    MatchPvpExpeditionsUseCase,
    PerformBattleActionUseCase,
    CreatePlayerUseCase,
    GenerateEventUseCase,
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
        self.notification_service = TelegramNotificationService(bot)

        # === Создаем Use Case ===

        # === Generate Event ===
        self.generate_event_uc = GenerateEventUseCase(self.random_provider)

        # === Battle ===
        self.start_battle_uc = StartBattleUseCase(self.notification_service)
        self.start_exp_uc = StartExpeditionUseCase(
            self.generate_event_uc, self.time_provider)
        self.complete_battle_uc = CompleteBattleUseCase()
        self.perform_battle_action_uc = PerformBattleActionUseCase(
            self.random_provider, self.complete_battle_uc)
        self.match_pvp_uc = MatchPvpExpeditionsUseCase()

        # === Expedition ===
        self.complete_exp_uc = CompleteExpeditionUseCase(
            self.start_battle_uc,
            self.time_provider,
            self.random_provider
        )
        self.get_active_exp_uc = GetActiveExpeditionUseCase()

        # === Player ===
        self.create_player_uc = CreatePlayerUseCase()

    def uow_factory(self):
        return SqlAlchemyUnitOfWork(self.session_maker)
    
    def create_background_tasks(self):
        """Создает фоновые задачи"""
        from ddd_fantasy_rpg.bot.aiogram_bot.background_tasks import (
            ExpeditionCompletionBackgroundTask,
            PvpMatchingBackgroundTask
        )

        expedition_task = ExpeditionCompletionBackgroundTask(
            complete_expetidion_use_case=self.complete_exp_uc,
            get_active_expedition_use_case=self.get_active_exp_uc,
            notification_service=self.notification_service,
            async_session_maker=self.session_maker
        )

        pvp_task = PvpMatchingBackgroundTask(
            match_pvp_use_case=self.match_pvp_uc,
            notification_service=self.notification_service,
            async_session_maker=self.session_maker
        )

        return {
            "expedition_completion": expedition_task,
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

            # Infrastructure
            unit_of_work_factory=self.uow_factory
        )
