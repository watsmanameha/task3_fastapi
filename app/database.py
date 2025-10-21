from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./glossary.db"
engine: AsyncEngine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
    class_=AsyncSession,
)


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    session: AsyncSession = SessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def create_all() -> None:
    """Create database tables asynchronously."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
