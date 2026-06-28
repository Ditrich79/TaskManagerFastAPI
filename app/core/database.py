from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings
from typing import Annotated

# Создаем асинхронный движок для PostgreSQL
engine = create_async_engine(settings.DATABASE_URL, echo=True, pool_pre_ping=True)

# Создаем фабрику сессий. Каждый запрос будет получать свою сессию для работы с БД.
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# Базовый класс для наших моделей SQLAlchemy
class Base(DeclarativeBase):
    pass

# Зависимость FastAPI, которая будет предоставлять сессию БД для каждого запроса
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

GetAsyncSession = Annotated[AsyncSession, Depends(get_db)]