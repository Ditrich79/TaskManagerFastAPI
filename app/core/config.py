from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Обязательные переменные (без значений по умолчанию)
    DATABASE_URL: str
    SECRET_KEY: str
    REDIS_URL: str

    # Переменные с безопасными значениями по умолчанию
    PROJECT_NAME: str = "Task Manager API"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # extra="ignore"  # игнорировать лишние переменные из .env (опционально)
    )

settings = Settings()