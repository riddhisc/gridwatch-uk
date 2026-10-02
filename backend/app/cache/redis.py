from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

from pydantic import BaseModel
from redis.asyncio import Redis

from app.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class CacheClient:

    def __init__(self, redis: Redis) -> None:
        self._redis = redis

    async def ping(self) -> bool:
        return bool(await self._redis.ping())

    async def get_json(self, key: str) -> Any | None:
        raw = await self._redis.get(key)
        if raw is None:
            return None
        return json.loads(raw)

    async def set_json(self, key: str, value: Any, ttl_seconds: int) -> None:
        payload = value.model_dump(mode="json") if isinstance(value, BaseModel) else value
        await self._redis.set(key, json.dumps(payload, default=str), ex=ttl_seconds)

    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Awaitable[T]],
        ttl_seconds: int,
    ) -> tuple[T, bool]:
        try:
            cached = await self.get_json(key)
        except Exception:
            logger.warning("cache_read_failed", extra={"key": key})
            return await factory(), False

        if cached is not None:
            return cached, True

        fresh = await factory()
        try:
            await self.set_json(key, fresh, ttl_seconds)
        except Exception:
            logger.warning("cache_write_failed", extra={"key": key})
        return fresh, False

    async def aclose(self) -> None:
        await self._redis.aclose()
