from aiogram import Router, F
from aiogram.types import CallbackQuery

from ddd_fantasy_rpg.bot.aiogram_bot.dependency_context import DependencyContext
from ddd_fantasy_rpg.domain.battle import BattleAction, BattleActionType
from ddd_fantasy_rpg.application.use_cases.perform_battle_action import BattleActionResult
from ddd_fantasy_rpg.domain.common import DomainError
from ddd_fantasy_rpg.infrastructure.unit_of_work import SqlAlchemyUnitOfWork


router = Router()


@router.callback_query(F.data.startswith("battle_attack_"))
async def handle_battle_attack(
    callback: CallbackQuery,
    dependencies: DependencyContext
):
    """Обрабатываем атаку в бою."""
    player_id = callback.data.split("_", 3)[2]
    
    if str(callback.from_user.id) != player_id:
        await callback.answer("Это не твой бой!", show_alert=True)
        return
    
    try:
        async with SqlAlchemyUnitOfWork(dependencies.async_session_maker) as uow:
            action = BattleAction(action_type=BattleActionType.ATTACK)
            result = await dependencies.perform_battle_action_use_case.execute(player_id, action, uow)
            await _send_battle_result(callback, result, dependencies, player_id)
    except DomainError as e:
        await callback.answer(str(e), show_alert=True)
    except Exception as e:
        await callback.answer(f"Ошибка: {e}", show_alert=True)
        
    await callback.answer()


@router.callback_query(F.data.startswith("battle_flee_"))
async def handle_battle_flee(
    callback: CallbackQuery,
    dependencies: DependencyContext

):
    """Обрабатываем попытку побега из боя."""
    player_id = callback.data.split("_", 3)[2]
    
    if str(callback.from_user.id) != player_id:
        await callback.answer("Это не твой бой!", show_alert=True)
        return
    
    try:
        async with SqlAlchemyUnitOfWork(dependencies.async_session_maker) as uow:
            action = BattleAction(action_type=BattleActionType.FLEE)
            result = await dependencies.perform_battle_action_use_case.execute(player_id, action, uow)
            await _send_battle_result(callback, result, dependencies, player_id)
    except DomainError as e:
        await callback.answer(str(e), show_alert=True)
    except Exception as e:
        await callback.answer(f"Ошибка: {e}", show_alert=True)
        
    await callback.answer()
    
    
@router.callback_query(F.data.startswith("battle_use_skill_"))
async def handle_battle_use_skill(
    callback: CallbackQuery,
    dependencies: DependencyContext
):
    """Обрабатываем использование скилла в бою."""
    parts = callback.data.split("_")

    if len(parts) < 5:
        raise ValueError("Неверный формат действия!")
    
    player_id = parts[3]
    
    if str(callback.from_user.id) != player_id:
        await callback.answer("Это не твой бой!", show_alert=True)
        return
    
    skill_name = parts[4]
    
    try:
        async with SqlAlchemyUnitOfWork(dependencies.async_session_maker) as uow:
            action = BattleAction(action_type=BattleActionType.USE_SKILL, skill_name=skill_name)
            result = await dependencies.perform_battle_action_use_case.execute(player_id, action, uow)
            await _send_battle_result(callback, result, dependencies, player_id)
    except DomainError as e:
        await callback.answer(str(e), show_alert=True)
    except Exception as e:
        await callback.answer(f"Ошибка: {e}", show_alert=True)
        
    await callback.answer()
  
    
@router.callback_query(F.data.startswith("battle_use_item_"))
async def handle_battle_use_item(
    callback: CallbackQuery,
    dependencies: DependencyContext
):
    """Обрабатываем использование предмета в бою."""
    parts = callback.data.split("_")

    if len(parts) < 5:
        raise ValueError("Неверный формат действия!")
    
    player_id = parts[3]
    
    if str(callback.from_user.id) != player_id:
        await callback.answer("Это не твой бой!", show_alert=True)
        return
    
    item_id = parts[4]
    
    try:
        async with SqlAlchemyUnitOfWork(dependencies.async_session_maker) as uow:
            action = BattleAction(action_type=BattleActionType.USE_ITEM, item_id=item_id)
            result = await dependencies.perform_battle_action_use_case.execute(player_id, action, uow)
            await _send_battle_result(callback, result, dependencies, player_id)
    except DomainError as e:
        await callback.answer(str(e), show_alert=True)
    except Exception as e:
        await callback.answer(f"Ошибка: {e}", show_alert=True)
        
    await callback.answer()
    

async def _send_battle_result(
    callback: CallbackQuery,
    result: BattleActionResult,
    dependencies:DependencyContext,
    player_id: str
):
    """Отправляем результат боя."""
    if result.is_finished:
        # Отправляем финальные уведомления
        await dependencies.notification_service.notify_battle_finished(
            battle_result=result
        )
        
        # отправляем основное сообщение о результате боя
        await callback.message.answer(result.message)
        
    else:
        
        # TODO: Починить теперь не отправляется сообщение для обычного хода
        # Оправляем уведомление текущему игроку
        await dependencies.notification_service.notify_battle_action_result(
            player_id=player_id,
            result=result,
            is_current_player=True
        )
        
        if result.requires_opponent_notification and result.opponent_id:
            await dependencies.notification_service.notify_battle_action_result(
                player_id=result.opponent_id,
                result=result,
                is_current_player=False
            )


