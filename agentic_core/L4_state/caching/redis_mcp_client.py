"""
Sovereign Redis MCP Client – Phase 16A (Dec 27, 2025)
Replaces all direct redis-py operations with official Redis MCP integration.
L3 routed, L5 shielded, L6 observable.
"""
import logging
from typing import Any, Optional, List, Dict

# Updated import path for current repo structure
from agentic_core.config.core.sovereign_config import get_sovereign_config

# Lazy import to attempt to mitigate circular dependency between L4 and L3
# if L3 imports L4 state components.
try:
    from agentic_core.L3_orchestration.workflow_engines.mcp_router_sovereign import SovereignMCPRouter
except ImportError:
    # Fallback or strict error depending on startup order
    pass

logger = logging.getLogger(__name__)


class SovereignRedisMCPClient:
    """Official Redis MCP client for sovereign caching operations."""

    def __init__(self, role: str = "state_cache"):
        config = get_sovereign_config()
        if not config.get_bool("REDIS_MCP_ENABLED", False):
            raise ValueError("Redis MCP disabled in sovereign config")

        # Initialize Router
        from agentic_core.L3_orchestration.workflow_engines.mcp_router_sovereign import SovereignMCPRouter
        self.router = SovereignMCPRouter(role=role)
        self.config = config
        logger.info("[L4 REDIS] Sovereign Redis MCP client initialized")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from sovereign cache via MCP."""
        if len(key) > self.config.get_int("REDIS_MAX_KEY_LENGTH", 250):
            raise ValueError(f"Key exceeds sovereign limit: {len(key)}")

        full_key = f"{self.config.get_str('REDIS_CACHE_PREFIX', 'agentic:')}{key}"

        try:
            result = await self.router.manager.call_tool(
                "mcp9_get",
                {"key": full_key}
            )
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

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in sovereign cache via MCP."""
        if len(key) > self.config.get_int("REDIS_MAX_KEY_LENGTH", 250):
            raise ValueError(f"Key exceeds sovereign limit: {len(key)}")

        full_key = f"{self.config.get_str('REDIS_CACHE_PREFIX', 'agentic:')}{key}"

        payload = {
            "key": full_key,
            "value": value,
            "expireSeconds": ttl or self.config.get_int("REDIS_DEFAULT_TTL_SECONDS", 3600)
        }

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
        full_key = f"{self.config.get_str('REDIS_CACHE_PREFIX', 'agentic:')}{key}"
        try:
            result = await self.router.manager.call_tool("mcp9_delete", {"key": full_key})
            if isinstance(result, dict):
                return result.get("deleted", 0) > 0
            return False
        except Exception as e:
            logger.error(f"[L4 REDIS] Cache DELETE failed for {key}: {e}")
            return False

    async def keys(self, pattern: str = "*") -> List[str]:
        """List keys matching pattern via MCP."""
        full_pattern = f"{self.config.get_str('REDIS_CACHE_PREFIX', 'agentic:')}{pattern}"
        try:
            result = await self.router.manager.call_tool("mcp9_list", {"pattern": full_pattern})
            return result.get("keys", []) if isinstance(result, dict) else []
        except Exception as e:
            logger.error(f"[L4 REDIS] Cache KEYS failed: {e}")
            return []


# Singleton instance
_redis_client: Optional[SovereignRedisMCPClient] = None


def get_redis_client() -> SovereignRedisMCPClient:
    """Get or create the global Redis MCP client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = SovereignRedisMCPClient()
    return _redis_client
