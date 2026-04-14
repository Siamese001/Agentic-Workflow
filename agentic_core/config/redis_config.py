"""Redis configuration with environment variable support."""

from __future__ import annotations

import os


def _read_int_env(name: str, default: int, *, minimum: int | None = None, maximum: int | None = None) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        value = default
    else:
        try:
            value = int(raw)
        except ValueError as exc:
            raise ValueError(f"Invalid integer for {name}: {raw}") from exc
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} must be >= {minimum}, got {value}")
    if maximum is not None and value > maximum:
        raise ValueError(f"{name} must be <= {maximum}, got {value}")
    return value


class RedisConnectionConfig:
    """Redis connection configuration."""

    def __init__(self):
        self.host = os.getenv("REDIS_HOST", "localhost").strip()
        self.port = _read_int_env("REDIS_PORT", 6379, minimum=1, maximum=65535)
        self.db = _read_int_env("REDIS_DB", 0, minimum=0)
        self.timeout = _read_int_env("REDIS_TIMEOUT", 5, minimum=1)


class ADGCacheConfig:
    """ADG cache-specific configuration."""

    def __init__(self):
        self.min_node_count = _read_int_env("ADG_MIN_NODE_COUNT", 8000, minimum=1)
        self.ingest_timeout = _read_int_env("ADG_INGEST_TIMEOUT", 120, minimum=1)


class RedisWindowsConfig:
    """Windows-specific Redis installation paths and startup configuration."""

    def __init__(self):
        default_paths = [
            r"C:\Program Files\Redis\redis-server.exe",
            r"C:\Program Files (x86)\Redis\redis-server.exe",
            r"C:\Redis\redis-server.exe",
        ]
        env_paths = os.getenv("REDIS_WINDOWS_PATHS")
        if env_paths:
            self.installation_paths = [path.strip() for path in env_paths.split(";") if path.strip()]
        else:
            self.installation_paths = default_paths

        self.service_start_timeout = _read_int_env("REDIS_SERVICE_START_TIMEOUT", 10, minimum=1)
        self.service_startup_delay = _read_int_env("REDIS_SERVICE_STARTUP_DELAY", 2, minimum=0)
        self.process_startup_delay = _read_int_env("REDIS_PROCESS_STARTUP_DELAY", 3, minimum=0)


def get_redis_config() -> RedisConnectionConfig:
    return RedisConnectionConfig()


def get_adg_cache_config() -> ADGCacheConfig:
    return ADGCacheConfig()


def get_redis_windows_config() -> RedisWindowsConfig:
    return RedisWindowsConfig()


__all__ = [
    "RedisConnectionConfig",
    "ADGCacheConfig",
    "RedisWindowsConfig",
    "get_redis_config",
    "get_adg_cache_config",
    "get_redis_windows_config",
]
