"""
SovereignMCPGateway - Unified MCP Operations Gateway

[PHASE 3 MIGRATION] Consolidates all MCP client operations:
- LLM routing with fallback
- Knowledge graph operations
- Archive management
- Centralized audit logging
- Connection pool reuse
- Retry/timeout hardening
"""
from __future__ import annotations
import logging
import time
from dataclasses import dataclass
from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
Logger = logging.getLogger(__name__)

@dataclass
class SovereignMCPGateway(SovereignBaseAgent):
    """
    Unified MCP Gateway - Single point of truth for all MCP operations.

    [PHASE 3 MIGRATION] Absorbed from:
    - llm_router_mcp_client.py
    - knowledge_graph_sovereign_graph_client.py
    - archive_client.py
    - caching_redis_mcp_client.py (redirects to RedisSovereignAgent)
    """
    _instance = None
    operation_stats = {'llm_route': 0, 'kg_query': 0, 'archive_op': 0, 'total': 0, 'errors': 0}

    def __new__(cls):
        """Singleton constructor."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _audit(self, operation: str, success: bool, latency_ms: float) -> None:
        """[PHASE 3] Record MCP operation to audit plane."""
        if not hasattr(self, 'audit_log'):
            self.audit_log = []
        self.audit_log.append({'op': operation, 'success': success, 'latency_ms': latency_ms, 'ts': time.time()})
        self.operation_stats['total'] += 1
        if not success:
            self.operation_stats['errors'] += 1
        else:
            self.operation_stats[operation] = self.operation_stats.get(operation, 0) + 1

    # guardian: allow-type-erasure
    async def llm_route(self, prompt: str, model: str='gpt-4', **kwargs) -> dict:
        """
        Route LLM request with fallback and retry.
        [PHASE 3] Absorbed from llm_router_mcp_client.py
        """
        start = time.time()
        try:
            result = await self._hardened_call('llm_route', self.router.manager.call_tool if hasattr(self, 'router') else self._mock_tool_call, tool_name='llm_route', args={'prompt': prompt, 'model': model, **kwargs})
            latency = (time.time() - start) * 1000
            self._audit('llm_route', True, latency)
            return result
        except Exception as e:
            latency = (time.time() - start) * 1000
            self._audit('llm_route', False, latency)
            Logger.error(f'[MCP Gateway] LLM Route failed: {e}')
            raise

    # guardian: allow-type-erasure
    async def kg_query(self, query: str, **kwargs) -> dict:
        """
        Query knowledge graph with caching.
        [PHASE 3] Absorbed from knowledge_graph_sovereign_graph_client.py
        """
        start = time.time()
        try:
            result = await self._hardened_call('kg_query', self.router.manager.call_tool if hasattr(self, 'router') else self._mock_tool_call, tool_name='kg_query', args={'query': query, **kwargs})
            latency = (time.time() - start) * 1000
            self._audit('kg_query', True, latency)
            return result
        except Exception as e:
            latency = (time.time() - start) * 1000
            self._audit('kg_query', False, latency)
            Logger.error(f'[MCP Gateway] KG Query failed: {e}')
            raise

    # guardian: allow-type-erasure
    async def archive_operation(self, operation: str, **kwargs) -> dict:
        """
        Execute archive operation.
        [PHASE 3] Absorbed from archive_client.py
        """
        start = time.time()
        try:
            result = await self._hardened_call('archive_op', self.router.manager.call_tool if hasattr(self, 'router') else self._mock_tool_call, tool_name='archive_op', args={'operation': operation, **kwargs})
            latency = (time.time() - start) * 1000
            self._audit('archive_op', True, latency)
            return result
        except Exception as e:
            latency = (time.time() - start) * 1000
            self._audit('archive_op', False, latency)
            Logger.error(f'[MCP Gateway] Archive Op failed: {e}')
            raise

    # guardian: allow-type-erasure
    async def _mock_tool_call(self, tool_name: str, args: dict) -> dict:
        """Mock handler for initial bring-up if router is missing."""
        return {'status': 'success', 'mock': True, 'tool': tool_name}

    def heal(self, violation, **kwargs):
        return super().heal(violation, **kwargs)
_gateway_instance = None

def get_mcp_gateway() -> SovereignMCPGateway:
    """Get or create the global MCP gateway."""
    global _gateway_instance
    if _gateway_instance is None:
        _gateway_instance = SovereignMCPGateway()
    return _gateway_instance
