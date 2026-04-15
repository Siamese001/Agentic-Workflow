"""Environment-backed Redis configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass

from .constants import DEFAULT_DB, DEFAULT_HOST, DEFAULT_PORT, DEFAULT_TIMEOUT_SECONDS


@dataclass(frozen=True)
class RedisConnectionConfig:
    """Configuration used to create a redis-py client."""

    host: str = DEFAULT_HOST
    port: int = DEFAULT_PORT
    db: int = DEFAULT_DB
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS

    @classmethod
    def from_env(cls) -> "RedisConnectionConfig":
        """Load Redis connection settings from environment variables."""
        return cls(
            host=os.getenv("REDIS_HOST", DEFAULT_HOST),
            port=int(os.getenv("REDIS_PORT", str(DEFAULT_PORT))),
            db=int(os.getenv("REDIS_DB", str(DEFAULT_DB))),
            timeout_seconds=float(os.getenv("REDIS_TIMEOUT", str(DEFAULT_TIMEOUT_SECONDS))),
        )
