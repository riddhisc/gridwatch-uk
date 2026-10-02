import pytest

from app.cache.redis import CacheClient


class FakeRedis:
    def __init__(self) -> None:
        self.data: dict[str, str] = {}

    async def ping(self) -> bool:
        return True

    async def get(self, key: str):
        return self.data.get(key)

    async def set(self, key: str, value: str, ex: int | None = None):
        self.data[key] = value
        return True

    async def aclose(self) -> None:
        return None


@pytest.mark.asyncio
async def test_cache_get_or_set_roundtrip() -> None:
    cache = CacheClient(FakeRedis())  # type: ignore[arg-type]
    calls = {"n": 0}

    async def factory():
        calls["n"] += 1
        return {"value": 42}

    first, first_cached = await cache.get_or_set("k", factory, 30)
    second, second_cached = await cache.get_or_set("k", factory, 30)
    assert first == {"value": 42}
    assert first_cached is False
    assert second["value"] == 42
    assert second_cached is True
    assert calls["n"] == 1


class BrokenRedis:
    async def get(self, key: str):
        raise ConnectionError("redis down")

    async def set(self, key: str, value: str, ex: int | None = None):
        raise ConnectionError("redis down")

    async def aclose(self) -> None:
        return None


@pytest.mark.asyncio
async def test_cache_falls_back_when_redis_is_down() -> None:
    cache = CacheClient(BrokenRedis())  # type: ignore[arg-type]

    async def factory():
        return {"value": 7}

    value, cached = await cache.get_or_set("k", factory, 30)
    assert value == {"value": 7}
    assert cached is False
