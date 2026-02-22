from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from ddd_fantasy_rpg.domain import ExpeditionDistance
from ddd_fantasy_rpg.domain.exceptions import PlayerAlreadyExistingError
from ddd_fantasy_rpg.infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from ddd_fantasy_rpg.application.use_cases.create_player import CreatePlayerUseCase
from ddd_fantasy_rpg.application.use_cases.start_expedition import StartExpeditionUseCase
from ddd_fantasy_rpg.application.async_factories import create_async_use_cases
from ddd_fantasy_rpg.bot.aiogram_bot.battle_handlers import router as battle_router

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}\n"  # type: ignore
        "Используй /create_player чтобы начать."
    )


@router.message(Command("create_player"))
async def cmd_create_player(
    message: Message,
    create_player_use_case: CreatePlayerUseCase,
    async_session_maker,
):
    user = message.from_user

    try:
        async with SqlAlchemyUnitOfWork(async_session_maker) as uow:
            player = await create_player_use_case.execute(
                player_id=str(user.id),
                telegram_id=user.id,
                name=user.first_name or f"User{user.id}",
                uow=uow
            )

            await message.answer(f"Создан персонаж: {player.name} ({player.profession.value})")

    except PlayerAlreadyExistingError:
        await message.answer("Ты уже в игре!")
    except Exception as e:
        await message.answer(f"Ошибка при создании персонажа: {e}")


@router.message(Command("expedition"))
async def cmd_expedition(
    message: Message,
    start_expedition_use_case: StartExpeditionUseCase,
    async_session_maker
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

    async with SqlAlchemyUnitOfWork(async_session_maker) as uow:
        try:
            await start_expedition_use_case.execute(str(message.from_user.id), distance, uow)
            await message.answer(
                f"Отправился в {distance_str} вылазку!\n"
                f"Вернёшься через {distance.duration_minutes} мин."
            )
        except Exception as e:
            await message.answer(f"Ошибка: {e}")


def register_handlers(dp):
    dp.include_router(router)
    dp.include_router(battle_router)