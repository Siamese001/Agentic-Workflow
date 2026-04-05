"""Redis configuration with environment variable support.

Provides centralized Redis configuration for ADG cache and coordination fabric.
All values can be overridden via environment variables.
"""

import os


class RedisConnectionConfig:
    """Redis connection configuration."""

    def __init__(self):
        """Load Redis configuration from environment variables."""
        self.host = os.getenv("REDIS_HOST", "localhost")
        self.port = int(os.getenv("REDIS_PORT", "6379"))
        self.db = int(os.getenv("REDIS_DB", "0"))
        self.timeout = int(os.getenv("REDIS_TIMEOUT", "5"))


class ADGCacheConfig:
    """ADG cache-specific configuration."""

    def __init__(self):
        """Load ADG cache configuration from environment variables."""
        self.min_node_count = int(os.getenv("ADG_MIN_NODE_COUNT", "8000"))
        self.ingest_timeout = int(os.getenv("ADG_INGEST_TIMEOUT", "120"))


class RedisWindowsConfig:
    """Windows-specific Redis installation paths and startup configuration."""

    def __init__(self):
        """Load Windows Redis paths and timing from environment or use defaults."""
        default_paths = [
            r"C:\Program Files\Redis\redis-server.exe",
            r"C:\Program Files (x86)\Redis\redis-server.exe",
            r"C:\Redis\redis-server.exe",
        ]
        # Allow override via environment variable (semicolon-separated)
        env_paths = os.getenv("REDIS_WINDOWS_PATHS")
        if env_paths:
            self.installation_paths = env_paths.split(";")
        else:
            self.installation_paths = default_paths

        # Startup timing configuration
        self.service_start_timeout = int(os.getenv("REDIS_SERVICE_START_TIMEOUT", "10"))
        self.service_startup_delay = int(os.getenv("REDIS_SERVICE_STARTUP_DELAY", "2"))
        self.process_startup_delay = int(os.getenv("REDIS_PROCESS_STARTUP_DELAY", "3"))


def get_redis_config() -> RedisConnectionConfig:
    """Get Redis connection configuration.

    Returns:
        RedisConnectionConfig instance with values from environment or defaults
    """
    return RedisConnectionConfig()


def get_adg_cache_config() -> ADGCacheConfig:
    """Get ADG cache configuration.

    Returns:
        ADGCacheConfig instance with values from environment or defaults
    """
    return ADGCacheConfig()


def get_redis_windows_config() -> RedisWindowsConfig:
    """Get Windows-specific Redis configuration.

    Returns:
        RedisWindowsConfig instance with values from environment or defaults
    """
    return RedisWindowsConfig()


__all__ = [
    "RedisConnectionConfig",
    "ADGCacheConfig",
    "RedisWindowsConfig",
    "get_redis_config",
    "get_adg_cache_config",
    "get_redis_windows_config",
]
