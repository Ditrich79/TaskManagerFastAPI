import asyncio
import sys
import fakeredis.aioredis

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings

# === Исправление для Windows: переключаем event loop на Selector ===
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

TEST_DATABASE_URL = settings.DATABASE_URL.replace(
    settings.DATABASE_URL.split("/")[-1], "task_manager_test"
)

@pytest_asyncio.fixture(scope="function")
async def engine():
    """Создаёт движок для каждого теста и гарантированно его закрывает."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture(scope="function")
async def db_session(engine):
    """Создаёт таблицы перед тестом и удаляет их после."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest_asyncio.fixture(scope="function")
async def auth_headers(client: AsyncClient):
    """
    Фикстура, которая создаёт тестового пользователя,
    логинит его и возвращает словарь с заголовком Authorization.
    """
    # Регистрируем
    await client.post("/api/v1/auth/register", json={
        "email": "taskuser@example.com",
        "password": "testpassword"
    })
    # Логинимся, получаем токен
    response = await client.post("/api/v1/auth/login", data={
        "username": "taskuser@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture(autouse=True)
async def mock_redis(monkeypatch):
    """Подменяет реальный Redis на фейковый для всех тестов."""
    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    
    async def fake_get_redis():
        return fake_redis

    monkeypatch.setattr("app.utils.cache.get_redis", fake_get_redis)
    # Также можно переопределить redis_pool, но проще заменить функцию get_redis
    await fake_redis.flushall()
    yield
    await fake_redis.flushall()