from aiogram import Router, F
from aiogram.types import CallbackQuery

from ddd_fantasy_rpg.domain.battle import BattleAction, BattleActionType
from ddd_fantasy_rpg.infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from ddd_fantasy_rpg.application.use_cases.perform_battle_action import PerformBattleActionUseCase
from ddd_fantasy_rpg.domain.notifications import NotificationService
from ddd_fantasy_rpg.domain.exceptions import DomainError

router = Router()


@router.callback_query(F.data.startswith("battle_attack_"))
async def handle_battle_attack(
    callback: CallbackQuery,
    perform_battle_action_use_case: PerformBattleActionUseCase,
    notification_service: NotificationService,
    async_session_maker
):
    """Обрабатываем атаку в бою."""
    player_id = callback.data.split("_", 3)[2]

    if str(callback.from_user.id) != player_id:
        await callback.answer("Это не твой бой!", show_alert=True)
        return
    
    action = BattleAction(action_type=BattleActionType.ATTACK)
    await _handle_battle_action(
        callback,
        player_id,
        action,
        perform_battle_action_use_case,
        notification_service,
        async_session_maker
    )

@router.callback_query(F.data.startswith("battle_flee_"))
async def handle_battle_flee(
    callback: CallbackQuery,
    perform_battle_action_use_case: PerformBattleActionUseCase,
    notification_service: NotificationService,
    async_session_maker
):
    """Обрабатываем попытку побега из боя."""
    player_id = callback.data.split("_", 3)[2]

    if str(callback.from_user.id) != player_id:
        await callback.answer("Это не твой бой!", show_alert=True)
        return
    
    action = BattleAction(action_type=BattleActionType.FLEE)
    await _handle_battle_action(
        callback,
        player_id,
        action,
        perform_battle_action_use_case,
        notification_service,
        async_session_maker
    )
    
@router.callback_query(F.data.startswith("battle_use_skill_"))
async def handle_battle_use_skill(
    callback: CallbackQuery,
    perform_battle_action_use_case: PerformBattleActionUseCase,
    notification_service: NotificationService,
    async_session_maker
):
    """Обрабатываем использование скилла в бою."""
    parts = callback.data.split("_", 4)
    
    if len(parts) < 5:
        await callback.answer("Неверный формат действия!", show_alert=True)
        return
    
    player_id = parts[3]
    skill_name = parts[4]
    
    if str(callback.from_user.id) != player_id:
        await callback.answer("Это не твой бой!", show_alert=True)
        return
    
    action = BattleAction(
        action_type=BattleActionType.USE_SKILL,
        skill_name=skill_name
    )
    
    await _handle_battle_action(
        callback,
        player_id,
        action,
        perform_battle_action_use_case,
        notification_service,
        async_session_maker
    )
    
@router.callback_query(F.data.startswith("battle_use_item_"))
async def handle_battle_use_item(
    callback: CallbackQuery,
    perform_battle_action_use_case: PerformBattleActionUseCase,
    notification_service: NotificationService,
    async_session_maker
):
    """Обрабатываем использование предмета в бою."""
    parts = callback.data.split("_", 4)
    
    if len(parts) < 5:
        await callback.answer("Неверный формат действия!", show_alert=True)
        return
    
    player_id = parts[3]
    item_id = parts[4]
    
    if str(callback.from_user.id) != player_id:
        await callback.answer("Это не твой бой!", show_alert=True)
        return
    
    action = BattleAction(
        action_type=BattleActionType.USE_ITEM,
        item_id=item_id
    )
    
    await _handle_battle_action(
        callback,
        player_id,
        action,
        perform_battle_action_use_case,
        notification_service,
        async_session_maker
    )
    
    
async def _handle_battle_action(
    callback: CallbackQuery,
    player_id: str,
    action: BattleAction,
    perform_battle_action_use_case: PerformBattleActionUseCase,
    notification_service: NotificationService,
    async_session_maker
):
    "Обрабатывает стандартное действие в бою."
    try:
        async with SqlAlchemyUnitOfWork(async_session_maker) as uow:
            result = await perform_battle_action_use_case.execute(player_id, action, uow)

            if result.is_finished:
                # Определяем участников боя для уведомления
                winner_id = None
                loser_id = None
                
                # Определяем победителя и проигравшего
                if result.battle_outcome.get("winner") == "player":
                    winner_id = player_id
                    # для PvPЖ проигравший - opponent_id для PvE: проигравший монстр (не игрок)
                    if result.battle_outcome.get("is_pvp"):
                        loser_id = result.opponent_id
                elif result.battle_outcome.get("player_died"):
                    loser_id = player_id
                    if result.battle_outcome.get("is_pvp")
                        winner_id = result.opponent_id
                
                # Отправляем финальные уведомления
                await notification_service.notify_battle_finished(
                    winner_id=winner_id,
                    loser_id=loser_id,
                    battle_outcome=result.battle_outcome
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
                
                # Для PvP отправляем уведомление противнику
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