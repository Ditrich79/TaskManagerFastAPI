import asyncio
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.crud import crud_user
from app.schemas.user import UserCreate

async def main():
    async with AsyncSessionLocal() as db:
        # Создать пользователя
        user_in = UserCreate(email="test@example.com", password="test")
        user = await crud_user.create_user(db, user=user_in)
        print(f"Создан пользователь: {user.email}")
        
        # Найти пользователя
        user = await crud_user.get_user_by_email(db, email="test@example.com")
        print(f"Найден пользователь с ID: {user.id}")

asyncio.run(main())