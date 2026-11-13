import os
# Force SQLite in-memory database for all pytest executions
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

import asyncio
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base, engine, AsyncSessionLocal, get_db
from app.main import app


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Provides a fresh, isolated database session with tables created for each test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    """Provides an asynchronous test client with the database session overridden."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def sync_client():
    """Provides a synchronous TestClient for testing WebSocket interactions with shared memory DB."""
    async def init():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    asyncio.run(init())

    with TestClient(app) as tc:
        yield tc

    async def drop():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    asyncio.run(drop())
