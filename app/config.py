from datetime import timedelta

from pydantic import NonNegativeInt, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

TIME_PERIODS = {
    "second": timedelta(seconds=1),
    "minute": timedelta(minutes=1),
    "hour": timedelta(hours=1),
    "day": timedelta(days=1),
    "week": timedelta(days=7),
    "month": timedelta(days=28),
    "year": timedelta(days=365),
}
FORBIDDEN_HEADERS = ["host", "content-length", "connection"]


class Settings(BaseSettings):
    redis_url: RedisDsn
    max_retries: NonNegativeInt = 3

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
