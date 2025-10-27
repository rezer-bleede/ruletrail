from __future__ import annotations

from datetime import datetime, timezone


def utcnow() -> datetime:
    """Return a timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


def iso_timestamp() -> str:
    """Return an ISO 8601 string for the current UTC time."""
    return utcnow().isoformat()
