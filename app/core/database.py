from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings
from typing import Annotated

# Создаем асинхронный движок для PostgreSQL
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# Создаем фабрику сессий. Каждый запрос будет получать свою сессию для работы с БД.
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Базовый класс для наших моделей SQLAlchemy
Base = declarative_base()

# Зависимость FastAPI, которая будет предоставлять сессию БД для каждого запроса
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


GetAsyncSession = Annotated[AsyncSession, Depends(get_db)]