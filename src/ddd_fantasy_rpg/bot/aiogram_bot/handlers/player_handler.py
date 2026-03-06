from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from ddd_fantasy_rpg.domain.player.exceptions import PlayerAlreadyExistingError
from ddd_fantasy_rpg.bot.aiogram_bot.dependency_context import DependencyContext

router = Router()


@router.message(Command("create_player"))
async def cmd_create_player(
    message: Message,
    dependencies: DependencyContext
):
    user = message.from_user

    try:
        await dependencies.create_player_use_case.execute(
            player_id=str(user.id),
            telegram_id=user.id,
            name=user.first_name or f"User{user.id}",
        )

    except PlayerAlreadyExistingError:
        await message.answer("Ты уже в игре!")
    except Exception as e:
        await message.answer(f"Ошибка при создании персонажа: {e}")
