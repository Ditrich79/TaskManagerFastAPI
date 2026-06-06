import json
from typing import Any, Optional

import redis.asyncio as redis
from app.core.config import settings


redis_pool = redis.ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)

async def get_redis() -> redis.Redis:
    """Возвращает клиент Redis, используя пул соединений."""
    return redis.Redis(connection_pool=redis_pool)

async def get_cache(key: str) -> Optional[Any]:
    """Получает значение из кеша и десериализует его из JSON."""
    redis = await get_redis()
    value = await redis.get(key)
    if value is None:
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value
    
async def set_cache(key: str, value: Any, expire: int = 60) -> None:
    """Сохраняет значение в кеш, сериализуя в JSON. Срок жизни — expire секунд."""
    redis = await get_redis()
    await redis.set(key, json.dumps(value), ex=expire)

async def invalidate_user_tasks_cache(user_id: int) -> None:
    """Удаляет все ключи кеша, связанные с задачами конкретного пользователя."""
    redis = await get_redis()
    # Ищем все ключи по шаблону
    keys = await redis.keys(f"user:{user_id}:task*")
    if keys:
        await redis.delete(*keys)