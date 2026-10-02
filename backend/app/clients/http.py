from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential_jitter

from app.core.errors import UpstreamAPIError
from app.core.logging import get_logger

logger = get_logger(__name__)

RETRYABLE_STATUS_CODES = {408, 429, 500, 502, 503, 504}


class RetryableHTTPError(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def _is_retryable(exc: BaseException) -> bool:
    return isinstance(
        exc,
        RetryableHTTPError | httpx.TimeoutException | httpx.NetworkError | httpx.RemoteProtocolError,
    )


class HttpClient:

    def __init__(
        self,
        *,
        base_url: str,
        timeout_seconds: float = 15.0,
        retry_attempts: int = 3,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        headers = {
            "User-Agent": "GreenPowerHours/0.1",
            "Accept": "application/json",
        }
        if extra_headers:
            headers.update(extra_headers)
        self._retry_attempts = retry_attempts
        self._client = httpx.AsyncClient(
            base_url=self._normalize_base(base_url),
            timeout=httpx.Timeout(timeout_seconds),
            headers=headers,
            follow_redirects=True,
        )

    @staticmethod
    def _normalize_base(base_url: str) -> str:
        return base_url.rstrip("/") + "/"

    @staticmethod
    def _normalize_path(path: str) -> str:
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return path.lstrip("/")

    async def aclose(self) -> None:
        await self._client.aclose()

    async def get_json(self, path: str, *, params: dict[str, Any] | None = None) -> Any:
        @retry(
            retry=retry_if_exception(_is_retryable),
            stop=stop_after_attempt(self._retry_attempts),
            wait=wait_exponential_jitter(initial=0.4, max=4.0),
            reraise=True,
        )
        async def _get() -> Any:
            try:
                response = await self._client.get(self._normalize_path(path), params=params)
            except httpx.RequestError as exc:
                logger.warning("upstream_request_failed", extra={"url": str(exc.request.url), "error": str(exc)})
                raise

            if response.status_code in RETRYABLE_STATUS_CODES:
                logger.warning(
                    "upstream_retryable_status",
                    extra={"url": str(response.url), "status": response.status_code},
                )
                raise RetryableHTTPError(
                    f"Retryable upstream status {response.status_code}",
                    status_code=response.status_code,
                )

            if response.is_error:
                raise UpstreamAPIError(
                    f"Upstream API error {response.status_code}: {response.text[:300]}",
                    status_code=response.status_code,
                    url=str(response.url),
                )

            return response.json()

        try:
            return await _get()
        except RetryableHTTPError as exc:
            raise UpstreamAPIError(
                f"Upstream API failed after retries: {exc}",
                status_code=exc.status_code,
                url=path,
            ) from exc
        except httpx.RequestError as exc:
            raise UpstreamAPIError(
                f"Upstream API request failed: {exc}",
                url=str(exc.request.url) if exc.request else path,
            ) from exc
