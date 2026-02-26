from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from ddd_fantasy_rpg.bot.aiogram_bot.dependency_context import DependencyContext
from ddd_fantasy_rpg.domain.expedition import ExpeditionDistance

router = Router()


@router.message(Command("expedition"))
async def cmd_expedition(
    message: Message,
    dependencies: DependencyContext
):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Укажи дальность: /expedition near")
        return

    distance_str = args[1].lower()
    distance_map = {
        "near": "NEAR",
        "medium": "MEDIUM",
        "far": "FAR"
    }
    if distance_str not in distance_map:
        await message.answer("Использу: near, medium, far")
        return

    distance = getattr(ExpeditionDistance, distance_map[distance_str])

    async with dependencies.unit_of_work() as uow:
        try:
            await dependencies.start_expedition_use_case.execute(str(message.from_user.id), distance, uow)
            await message.answer(
                f"Отправился в {distance_str} вылазку!\n"
                f"Вернёшься через {distance.duration_minutes} мин."
            )
        except Exception as e:
            await message.answer(f"Ошибка: {e}")

