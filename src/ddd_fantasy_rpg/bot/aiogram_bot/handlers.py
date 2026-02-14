from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from ddd_fantasy_rpg.domain import Player, Race, PlayerClass, ExpeditionDistance
from ddd_fantasy_rpg.application.async_factories import create_async_use_cases
from ddd_fantasy_rpg.bot.aiogram_bot.battle_handlers import router as battle_router

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}\n" # type: ignore
        "Используй /create_player чтобы начать."
    )
    
@router.message(Command("create_player"))
async def cmd_create_player(message: Message, async_session_maker):
    user = message.from_user
    async with async_session_maker() as session:
        use_cases = create_async_use_cases(session)
        player_repo = use_cases["start_expedition"]._player_repo
        
        existing = await player_repo.get_by_id(str(user.id)) # type: ignore
        if existing:
            await message.answer("Ты уже в игре!")
            return
        
        player = Player(
            player_id=str(user.id),
            telegram_id=user.id,
            name=user.first_name,
            race=Race.HUMAN,
            player_class=PlayerClass.WARRIOR,
        )
        
        await player_repo.save(player)
        
        await message.answer(f"Создан персонаж: {player._name} (Воин)")
        
@router.message(Command("expedition"))
async def cmd_expedition(message: Message, async_session_maker):
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
    
    async with async_session_maker() as session:
        use_cases = create_async_use_cases(session)
        try:
            await use_cases["start_expedition"].execute(str(message.from_user.id), distance)
            await message.answer(
                f"Отправился в {distance_str} вылазку!\n"
                f"Вернёшься через {distance.duration_minutes} мин."
            )
        except Exception as e:
            await message.answer(f"Ошибка: {e}")
            
def register_handlers(dp):
    dp.include_router(router) 
    dp.include_router(battle_router)
    