from __future__ import annotations
"""Automatic Fallback Manager for Tool Providers.

Phase 3 - Pillar 8 (Cont.): Tool Ecosystem (Automatic Fallbacks)
Implements ordered fallback chains when primary providers fail.
"""
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Awaitable, Callable, Dict, List, Optional, Protocol
from agentic_core.utils.core_extensions.timeout_decorator import timeout
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
Logger: Any = logging.getLogger(__name__)

class FallbackStrategy(Enum):
    """Fallback strategies."""
    SEQUENTIAL: Any = 'sequential'
    PARALLEL: Any = 'parallel'
    WEIGHTED: Any = 'weighted'

@dataclass
class ToolProvider:
    """Tool Provider configuration."""
    name: str
    execute_fn: Callable[[Dict[str, Any]], Awaitable[Any]]
    priority: int = 0
    circuit_breaker: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_available(self) -> bool:
        """Check if Provider is available.

        Returns:
            True if available (circuit not open)
        """
        if self.circuit_breaker:
            return self.circuit_breaker.can_execute()
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'name': self.name, 'priority': self.priority, 'available': self.is_available(), 'circuit_state': self.circuit_breaker.state if self.circuit_breaker else 'N/A', 'metadata': self.metadata}

@dataclass
class FallbackResult:
    """Result from fallback execution."""
    success: bool
    provider_used: str
    output: Any = None
    error: Optional[str] = None
    attempts: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {'success': self.success, 'provider_used': self.provider_used, 'output': self.output, 'error': self.error, 'attempts': self.attempts, 'metadata': self.metadata}

class FallbackManagerAgent(MCPHardenedMixin, SubatomicTestingMixin, HealerMixin):
    """Manages automatic fallback chains for tool providers.

    Features:
    - Ordered Provider sequences (e.g., Google → Bing → DuckDuckGo)
    - Circuit breaker integration
    - Automatic retry with next Provider
    - Fallback strategy selection
    - Execution tracking
    """

    def __init__(self, strategy: FallbackStrategy=FallbackStrategy.SEQUENTIAL, enable_logging: bool=True) -> None:
        """Initialize fallback manager.

        Args:
            strategy: Fallback strategy
            enable_logging: Enable logging
        """
        self.strategy = strategy
        self.enable_logging = enable_logging
        self._fallback_chains: Dict[str, List[ToolProvider]] = {}
        if self.enable_logging:
            LOGGER.info('fallback_manager_initialized', extra={'strategy': strategy.value})

    def register_chain(self, tool_name: str, providers: List[ToolProvider]) -> None:
        """Register a fallback chain for a tool.

        Args:
            tool_name: Name of the tool
            providers: Ordered list of providers
        """
        providers.sort(key=lambda p: p.priority, reverse=True)
        self._fallback_chains[tool_name] = providers
        if self.enable_logging:
            LOGGER.info('fallback_chain_registered', extra={'tool_name': tool_name, 'provider_count': len(providers), 'providers': [p.name for p in providers]})

    async def execute_with_fallback(self, tool_name: str, parameters: Dict[str, Any], max_attempts: Optional[int]=None) -> FallbackResult:
        """Execute tool with automatic fallback.

        Args:
            tool_name: Name of the tool
            parameters: Tool parameters
            max_attempts: Maximum fallback attempts

        Returns:
            FallbackResult
        """
        providers: Any = self._fallback_chains.get(tool_name, [])
        if not providers:
            return FallbackResult(success=False, provider_used='none', error=f'No providers registered for tool: {tool_name}')
        max_attempts: Any = max_attempts or len(providers)
        attempts: Any = []
        self._log_fallback_start(tool_name, providers)
        for i, Provider in enumerate(providers[:max_attempts]):
            if not Provider.is_available():
                self._handle_unavailable_provider(tool_name, Provider, attempts)
                continue
            result: Any = await self._try_provider(tool_name, Provider, parameters, i, attempts)
            if result:
                return result
        return self._handle_all_providers_failed(tool_name, attempts)

    def _log_fallback_start(self, tool_name: str, providers: List) -> None:
        """Log fallback execution start."""
        if self.enable_logging:
            LOGGER.info('executing_with_fallback', extra={'tool_name': tool_name, 'provider_count': len(providers)})

    def _handle_unavailable_provider(self, tool_name: str, Provider, attempts: List) -> None:
        """Handle unavailable Provider."""
        attempts.append({'Provider': Provider.name, 'skipped': True, 'reason': 'Circuit breaker open'})
        if self.enable_logging:
            LOGGER.warning('provider_skipped', extra={'tool_name': tool_name, 'Provider': Provider.name, 'reason': 'circuit_breaker_open'})

    async def _try_provider(self, tool_name: str, Provider, parameters: Dict, attempt_num: int, attempts: List) -> Optional[FallbackResult]:
        """Try executing with a Provider."""
        try:
            if self.enable_logging:
                LOGGER.debug('trying_provider', extra={'tool_name': tool_name, 'Provider': Provider.name, 'attempt': attempt_num + 1})
            output = await Provider.execute_fn(parameters)
            attempts.append({'Provider': Provider.name, 'success': True, 'output': output})
            if Provider.circuit_breaker:
                Provider.circuit_breaker.record_success()
            if self.enable_logging:
                LOGGER.info('provider_succeeded', extra={'tool_name': tool_name, 'Provider': Provider.name, 'attempt': attempt_num + 1})
            return FallbackResult(success=True, provider_used=Provider.name, output=output, attempts=attempts, metadata={'total_attempts': len(attempts), 'fallback_used': attempt_num > 0})
        except Exception as e:
            attempts.append({'Provider': Provider.name, 'success': False, 'error': str(e)})
            if Provider.circuit_breaker:
                Provider.circuit_breaker.record_failure()
            if self.enable_logging:
                LOGGER.warning('provider_failed', extra={'tool_name': tool_name, 'Provider': Provider.name, 'error': str(e), 'attempt': attempt_num + 1})
            return None

    def _handle_all_providers_failed(self, tool_name: str, attempts: List) -> FallbackResult:
        """Handle all providers failed."""
        if self.enable_logging:
            LOGGER.error('all_providers_failed', extra={'tool_name': tool_name, 'attempts': len(attempts)})
        return FallbackResult(success=False, provider_used='none', error='All providers failed', attempts=attempts, metadata={'total_attempts': len(attempts)})

    def get_chain(self, tool_name: str) -> List[ToolProvider]:
        """Get fallback chain for a tool.

        Args:
            tool_name: Tool name

        Returns:
            List of providers
        """
        return self._fallback_chains.get(tool_name, [])

    def get_available_providers(self, tool_name: str) -> List[ToolProvider]:
        """Get available providers for a tool.

        Args:
            tool_name: Tool name

        Returns:
            List of available providers
        """
        providers: Any = self._fallback_chains.get(tool_name, [])
        return [p for p in providers if p.is_available()]

    @timeout(300)
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L2 execution agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L2 execution - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

def create_fallback_manager(strategy: FallbackStrategy=FallbackStrategy.SEQUENTIAL) -> FallbackManagerAgent:
    """Factory function to create fallback manager.

    # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
    super().heal_repository()

    Args:
        strategy: Fallback strategy to use

    Returns:
        FallbackManagerAgent instance
    """
    return FallbackManagerAgent(strategy=strategy)

def get_fallback_manager() -> FallbackManagerAgent:
    """Factory function to get fallback manager instance."""
    return FallbackManagerAgent()
