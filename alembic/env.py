import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config, create_async_engine

from alembic import context

# Импортируем настройки FastAPI и базовый класс для моделей
from app.core.config import settings
from app.core.database import Base

# Импортируем все модели, чтобы Alembic мог их "видеть" и отслеживать изменения.
# Важно: импортировать нужно все модули, где определены модели SQLAlchemy.
from app.models.user import User
from app.models.task import Task

# ------------------------------------------------------------------------------
# Настройка объекта Alembic Config
# ------------------------------------------------------------------------------
config = context.config

# Устанавливаем URL базы данных из нашего приложения FastAPI.
# Это позволяет не дублировать конфигурацию и следовать принципу 12-факторных приложений.
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)

# Настройка логирования, как в официальном примере Alembic
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Указываем метаданные, которые будут использоваться для `autogenerate`
target_metadata = Base.metadata

# ------------------------------------------------------------------------------
# Функции для запуска миграций
# ------------------------------------------------------------------------------
def run_migrations_offline() -> None:
    """Запуск миграций в 'офлайн' режиме.
    Этот режим генерирует SQL-скрипт без подключения к базе данных.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    """Вспомогательная функция для запуска миграций в синхронном контексте."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """Запуск миграций в 'онлайн' режиме с асинхронным движком."""
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # `connection.run_sync` выполняет синхронную функцию внутри асинхронного контекста
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Запускает асинхронную функцию в синхронном контексте Alembic."""
    asyncio.run(run_async_migrations())

# ------------------------------------------------------------------------------
# Запуск Alembic
# ------------------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()