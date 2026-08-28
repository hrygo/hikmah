"""Pytest configuration and shared test fixtures."""

from collections.abc import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from hikmah.models.base import Base, async_session_factory, engine


@pytest_asyncio.fixture(autouse=True)
async def init_test_db() -> AsyncGenerator[None]:
    """Ensure database tables exist before each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession]:
    """Provide a clean test database session."""
    async with async_session_factory() as session:
        yield session
