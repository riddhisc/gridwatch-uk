from __future__ import annotations

from datetime import UTC, datetime


class UpstreamAPIError(Exception):
    """Raised when an upstream energy API returns a non-retryable error."""

    def __init__(
        self, message: str, *, status_code: int | None = None, url: str | None = None
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.url = url


def utcnow() -> datetime:
    return datetime.now(UTC)


def format_ci_datetime(value: datetime) -> str:
    """Carbon Intensity API expects compact UTC timestamps such as 2026-09-19T12:00Z."""
    aware = value.astimezone(UTC)
    return aware.strftime("%Y-%m-%dT%H:%MZ")


def format_octopus_datetime(value: datetime) -> str:
    aware = value.astimezone(UTC)
    return aware.strftime("%Y-%m-%dT%H:%M:%SZ")
