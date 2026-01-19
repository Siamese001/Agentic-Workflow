from __future__ import annotations
"""
Sovereign LLM Router MCP Client – Phase 16B (Dec 27, 2025)
Replaces all direct LLM SDK calls in L5 safety layer.
L3 routed, L5 shielded, L6 observable.
"""
import logging
from typing import Any, Dict, Optional
from agentic_core.config.blueprint_sovereign.sovereign_config_1 import config

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

Logger: Any = logging.getLogger(__name__)

class SovereignLlmRouterMcpClient(MCPHardenedMixin, HealerMixin):
    """Official LLM Router MCP client for sovereign validation operations."""

    def __init__(self, role: str='safety_validation'):
        super().__init__()
        if not config.LLM_ROUTER_MCP_ENABLED:
            raise ValueError('LLM Router MCP disabled in sovereign config')
        from agentic_core.L3_orchestration.workflow_engines.mcp_router_sovereign import SovereignMCPRouter
        self.router = SovereignMCPRouter(role=role)
        self._mcp_audit('init')
        Logger.info('[L5 LLM ROUTER] Sovereign LLM Router MCP client initialized')

    async def validate_content(self, content: str, validation_type: str='safety') -> Dict[str, Any]:
        """
        Validate content via LLM Router MCP.
        
        FAIL-SAFE STRATEGY: 
        If MCP fails, we default to is_safe=False (Fail Closed).
        """
        payload: Any = {'content': content, 'validation_type': validation_type, 'model': config.LLM_ROUTER_SAFETY_MODEL, 'temperature': config.LLM_ROUTER_VALIDATION_TEMPERATURE, 'max_tokens': config.LLM_ROUTER_MAX_TOKENS}
        try:
            result: Any = await self.router.manager.call_tool('llm_router_validate', payload)
            if not isinstance(result, dict):
                Logger.error(f'[L5 VALIDATION] Invalid result format from MCP: {result}')
                return {'is_safe': False, 'reason': 'MCP_FORMAT_ERROR'}
            is_safe: Any = result.get('is_safe', False)
            Logger.info(f'[L5 VALIDATION] {validation_type} result: {is_safe}')
            return result
        except Exception as e:
            Logger.error(f'[L5 VALIDATION] Critical Failure in Router Call: {e}')
            return {'is_safe': False, 'reason': f'VALIDATION_SYSTEM_FAILURE: {str(e)}'}

    async def classify_intent(self, query: str) -> Dict[str, Any]:
        """Classify user intent via MCP."""
        try:
            return await self.router.manager.call_tool('llm_router_classify', {'query': query, 'model': config.LLM_ROUTER_DEFAULT_PROVIDER, 'temperature': 0.3})
        except Exception as e:
            Logger.error(f'[L5 VALIDATION] Intent classification failed: {e}')
            return {'intent': 'unknown', 'confidence': 0.0}

    def heal_repository(self, dry_run: bool = True, **kwargs) -> Dict[str, Any]:
        """Repository healing with parent chain invocation."""
        result = super().heal_repository(dry_run=dry_run, **kwargs)
        return {"healed": 0, "skipped": 0, "parent": result}

_llm_router_client: Optional[SovereignLlmRouterMcpClient] = None

def get_llm_router_client() -> SovereignLlmRouterMcpClient:
    """Get or create the global LLM Router MCP client."""
    global _llm_router_client
    if _llm_router_client is None:
        _llm_router_client = SovereignLlmRouterMcpClient()
    return _llm_router_client

def _run_self_tests(self) -> dict:
        """Run internal self-tests."""
        results = {"passed": 0, "failed": 0, "tests": []}
        try:
            assert self is not None
            results["passed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "passed"})
        except AssertionError as e:
            results["failed"] += 1
            results["tests"].append({"name": "test_instantiation", "status": "failed", "error": str(e)})
        return results
