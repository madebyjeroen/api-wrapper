from datetime import datetime, timedelta

from redis import asyncio as redis

from app.config import settings

redis = redis.from_url(str(settings.redis_url), decode_responses=True)


async def update_session(key: str, date: datetime, lifetime: timedelta):
    async with redis.pipeline() as pipe:
        await (
            pipe.rpush(key, date.isoformat())
            .expire(key, int(lifetime.total_seconds()))
            .execute()
        )


async def retrieve_session(key: str):
    return await redis.lrange(key, 0, -1)
