from aiogram import Router, F
from aiogram.types import CallbackQuery

from ddd_fantasy_rpg.domain.battle import BattleAction, BattleActionType
from ddd_fantasy_rpg.infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from ddd_fantasy_rpg.application.use_cases.perform_battle_action import PerformBattleActionUseCase
from ddd_fantasy_rpg.domain.notifications import NotificationService
from ddd_fantasy_rpg.domain.exceptions import DomainError

router = Router()


@router.callback_query(F.data.startswith("battle_"))
async def handle_battle_action(
    callback: CallbackQuery,
    perform_battle_action_use_case: PerformBattleActionUseCase,
    notification_service: NotificationService,
    async_session_maker
):
    _, player_id, action_type = callback.data.split("_", 2)

    if str(callback.from_user.id) != player_id:
        await callback.answer("Это не твой бой!", show_alert=True)
        return
    try:
        async with SqlAlchemyUnitOfWork(async_session_maker) as uow:
            action = BattleAction(action_type=BattleActionType(action_type))
            result = await perform_battle_action_use_case.execute(player_id, action, uow)

            if result.is_finished:
                
                # Определяем победителя и проигравшего
                if result.battle_outcome and result.battle_outcome.get("winner") == "player":
                    winner_id = player_id
                    loser_id = result.opponent_id if result.opponent_id else player_id
                elif result.battle_outcome and result.battle_outcome.get("player_died"):
                    winner_id = result.opponent_id if result.opponent_id else "monster"
                    loser_id = player_id
                
                # Отправляем финальные уведомления
                if winner_id != "monster": # Если победил игрок
                    await notification_service.notify_battle_finished(
                        winner_id=winner_id,
                        loser_id=loser_id,
                        battle_outcone=result.battle_outcome
                    )
                else: # Если победил монстер
                    await notification_service.notify_battle_finished(
                        winner_id="monster",
                        loser_id=loser_id,
                        battle_outcone=result.battle_outcome
                    )
                
                # Отправляем основное сообщение
                await callback.message.answer(result.message)
                
            else:
                # отправляем уведомление текущему игроку
                
                await notification_service.notify_battle_action_result(
                    player_id=player_id,
                    result=result,
                    is_current_player=True
                )
                
                if result.requires_opponent_notification and result.opponent_id:
                    await notification_service.notify_battle_action_result(
                        player_id=result.opponent_id,
                        result=result,
                        is_current_player=False
                    )

    except DomainError as e:
        await callback.answer(str(e), show_alert=True)
    except Exception as e:
        await callback.answer(f"Ошибка: {e}", show_alert=True)

    await callback.answer()