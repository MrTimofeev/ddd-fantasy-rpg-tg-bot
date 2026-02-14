from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from ddd_fantasy_rpg.infrastructure.database.models import Base


def get_async_sessionmaker(db_path: str = "sqlite+aiosqlite:///game.db"):
    engine = create_async_engine(
        db_path,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool if ":memory:" in db_path else None,
        echo=False
    )
    
    async_sessionmaker_ = async_sessionmaker(engine, expire_on_commit=False)
    
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    return async_sessionmaker_, init_models