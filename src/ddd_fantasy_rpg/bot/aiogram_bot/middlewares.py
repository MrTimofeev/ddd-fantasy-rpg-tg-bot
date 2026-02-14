from collections.abc import Awaitable, Callable
from typing import Any
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker

class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker):
        super().__init__()
        self.session_pool = session_pool
        
    async def __call__(self, hadler, event: TelegramObject, data: dict):
        async with self.session_pool() as session:
            data["async_session"] = session
            return await hadler(event, data)