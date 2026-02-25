"""
Sovereign Redis MCP Client – Phase 16A (Dec 27, 2025)
Replaces all direct redis-py operations with official Redis MCP integration.
L3 routed, L5 shielded, L6 observable.
"""

import logging
from typing import Any

from agentic_core.config.blueprint_sovereign.environments.sovereign_config import config

# Lazy import to attempt to mitigate circular dependency between L4 and L3
# if L3 imports L4 state components.
try:
    from agentic_core.L3_orchestration.workflow_engines.mcp_router_sovereign import (
        SovereignMCPRouter,  # noqa: F401
    )
except ImportError:
    # Fallback or strict error depending on startup order
    pass

logger = logging.getLogger(__name__)


class SovereignRedisMCPClient:
    """Official Redis MCP client for sovereign caching operations."""

    def __init__(self, role: str = "state_cache"):
        if not config.REDIS_MCP_ENABLED:
            raise ValueError("Redis MCP disabled in sovereign config")

        # Initialize Router
        from agentic_core.L3_orchestration.workflow_engines.mcp_router_sovereign import SovereignMCPRouter

        self.router = SovereignMCPRouter(role=role)
        logger.info("[L4 REDIS] Sovereign Redis MCP client initialized")

    async def get(self, key: str) -> Any | None:
        """Get value from sovereign cache via MCP."""
        if len(key) > config.REDIS_MAX_KEY_LENGTH:
            raise ValueError(f"Key exceeds sovereign limit: {len(key)}")

        full_key = f"{config.REDIS_CACHE_PREFIX}{key}"

        try:
            result = await self.router.manager.call_tool("mcp9_get", {"key": full_key})
            # Handle MCP tool result structure
            if not result:
                return None

            # Assuming MCP returns specific dict structure, handle robustly
            if isinstance(result, dict):
                return result.get("value")
            return result

        except Exception as e:
            logger.error(f"[L4 REDIS] Cache GET failed for {key}: {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set value in sovereign cache via MCP."""
        if len(key) > config.REDIS_MAX_KEY_LENGTH:
            raise ValueError(f"Key exceeds sovereign limit: {len(key)}")

        full_key = f"{config.REDIS_CACHE_PREFIX}{key}"

        payload = {"key": full_key, "value": value, "expireSeconds": ttl or config.REDIS_DEFAULT_TTL_SECONDS}

        try:
            result = await self.router.manager.call_tool("mcp9_set", payload)
            # Strict checking on success status
            if isinstance(result, dict):
                return result.get("status") == "success"
            return bool(result)
        except Exception as e:
            logger.error(f"[L4 REDIS] Cache SET failed for {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from sovereign cache via MCP."""
        full_key = f"{config.REDIS_CACHE_PREFIX}{key}"
        try:
            result = await self.router.manager.call_tool("mcp9_delete", {"key": full_key})
            if isinstance(result, dict):
                return result.get("deleted", 0) > 0
            return False
        except Exception as e:
            logger.error(f"[L4 REDIS] Cache DELETE failed for {key}: {e}")
            return False

    async def keys(self, pattern: str = "*") -> list[str]:
        """List keys matching pattern via MCP."""
        full_pattern = f"{config.REDIS_CACHE_PREFIX}{pattern}"
        try:
            result = await self.router.manager.call_tool("mcp9_list", {"pattern": full_pattern})
            return result.get("keys", []) if isinstance(result, dict) else []
        except Exception as e:
            logger.error(f"[L4 REDIS] Cache KEYS failed: {e}")
            return []


# Singleton instance
_redis_client: SovereignRedisMCPClient | None = None


def get_redis_client() -> SovereignRedisMCPClient:
    """Get or create the global Redis MCP client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = SovereignRedisMCPClient()
    return _redis_client
