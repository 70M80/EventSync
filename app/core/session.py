from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
from app.core.config import settings

engine = create_async_engine(
    settings.async_database_url,
    pool_size=settings.engine_pool_size,
    max_overflow=settings.engine_max_overflow,
    pool_pre_ping=True,
    poolclass=AsyncAdaptedQueuePool,
    connect_args={
        "timeout": settings.db_timeout,
        "command_timeout": settings.command_timeout,
        "server_settings": {
            "statement_timeout": settings.statement_timeout,
        },
    },
)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        yield db
