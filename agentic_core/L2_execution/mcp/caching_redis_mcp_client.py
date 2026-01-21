from __future__ import annotations
"""
Sovereign Redis MCP Client – Phase 16A (Dec 27, 2025)
Replaces all direct redis-py operations with official Redis MCP integration.
L3 routed, L5 shielded, L6 observable.

[HARDENING] Added MCPHardenedMixin for retry, timeout, and observability (Jan 1, 2026)
"""
import logging
from typing import Any, Optional, List, Dict
from agentic_core.config.blueprint_sovereign.sovereign_config_1 import config
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.L4_state.validation_context.l4_subatomic_testing_mixin import L4SubatomicTestingMixin

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

Logger: Any = logging.getLogger(__name__)

class SovereignRedisMcpClient(MCPHardenedMixin, HealerMixin, L4SubatomicTestingMixin):
    """Official Redis MCP client for sovereign caching operations.

    [HARDENING] Inherits MCPHardenedMixin for:
    - Exponential backoff retry (3 attempts)
    - SovereignEvent emission on connect/fail/success
    - Timeout enforcement
    - CRITIQUE emission on exhausted retries
    """

    def __init__(self, role: str='state_cache'):
        super().__init__()
        if not config.REDIS_MCP_ENABLED:
            raise ValueError('Redis MCP disabled in sovereign config')
        from agentic_core.L3_orchestration.workflow_engines.SovereignMcpRouter import SovereignMcpRouter
        self.router = SovereignMcpRouter(role=role)
        self._mcp_audit('init')
        Logger.info('[L4 REDIS] Sovereign Redis MCP client initialized')

    async def get(self, key: str) -> Optional[Any]:
        """Get value from sovereign cache via MCP with hardened retry."""
        if len(key) > config.REDIS_MAX_KEY_LENGTH:
            raise ValueError(f'Key exceeds sovereign limit: {len(key)}')
        full_key: Any = f'{config.REDIS_CACHE_PREFIX}{key}'
        try:
            result: Any = await self._hardened_call(
                'redis_get',
                self.router.manager.call_tool,
                'mcp9_get',
                {'key': full_key}
            )
            if not result:
                return None
            if isinstance(result, dict):
                return result.get('value')
            return result
        except Exception as e:
            Logger.error(f'[L4 REDIS] Cache GET failed for {key}: {e}')
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int]=None) -> bool:
        """Set value in sovereign cache via MCP with hardened retry."""
        if len(key) > config.REDIS_MAX_KEY_LENGTH:
            raise ValueError(f'Key exceeds sovereign limit: {len(key)}')
        full_key: Any = f'{config.REDIS_CACHE_PREFIX}{key}'
        payload: Any = {'key': full_key, 'value': value, 'expireSeconds': ttl or config.REDIS_DEFAULT_TTL_SECONDS}
        try:
            result: Any = await self._hardened_call(
                'redis_set',
                self.router.manager.call_tool,
                'mcp9_set',
                payload
            )
            if isinstance(result, dict):
                return result.get('status') == 'success'
            return bool(result)
        except Exception as e:
            Logger.error(f'[L4 REDIS] Cache SET failed for {key}: {e}')
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from sovereign cache via MCP with hardened retry."""
        full_key: Any = f'{config.REDIS_CACHE_PREFIX}{key}'
        try:
            result: Any = await self._hardened_call(
                'redis_delete',
                self.router.manager.call_tool,
                'mcp9_delete',
                {'key': full_key}
            )
            if isinstance(result, dict):
                return result.get('deleted', 0) > 0
            return False
        except Exception as e:
            Logger.error(f'[L4 REDIS] Cache DELETE failed for {key}: {e}')
            return False

    async def keys(self, pattern: str='*') -> List[str]:
        """List keys matching pattern via MCP with hardened retry."""
        full_pattern: Any = f'{config.REDIS_CACHE_PREFIX}{pattern}'
        try:
            result: Any = await self._hardened_call(
                'redis_keys',
                self.router.manager.call_tool,
                'mcp9_list',
                {'pattern': full_pattern}
            )
            return result.get('keys', []) if isinstance(result, dict) else []
        except Exception as e:
            Logger.error(f'[L4 REDIS] Cache KEYS failed: {e}')
            return []

    def heal_repository(self) -> dict:
            """Invoke healing chain via super()."""
            return super().heal_repository()

_redis_client: Optional[SovereignRedisMCPClient] = None

def get_redis_client() -> SovereignRedisMCPClient:
    """Get or create the global Redis MCP client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = SovereignRedisMCPClient()
    return _redis_client
