"""Automatic Fallback Manager for Tool Providers.

Phase 3 - Pillar 8 (Cont.): Tool Ecosystem (Automatic Fallbacks)
Implements ordered fallback chains when primary providers fail.
"""

import logging
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional
from dataclasses import dataclass, field # Added import for dataclass and field

LOGGER = logging.getLogger(__name__)

class FallbackStrategy(Enum):
    """Fallback strategies."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    WEIGHTED = "weighted"

@dataclass
class ToolProvider:
    """Tool provider configuration."""
    name: str
    execute_fn: Callable[[Dict[str, Any]], Awaitable[Any]]
    priority: int = 0 # Changed PRIORITY to priority, INT to int
    circuit_breaker: Optional[Any] = None # Changed CircuitBreaker to Any as it's not defined
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_available(self) -> bool:
        """Check if provider is available.

        Returns:
            True if available (circuit not open)
        """
        if self.circuit_breaker:
            return self.circuit_breaker.can_execute()
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "priority": self.priority,
            "available": self.is_available(),
            "circuit_state": self.circuit_breaker.state if self.circuit_breaker else "N/A",
            "metadata": self.metadata,
        }

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
        return {
            "success": self.success,
            "provider_used": self.provider_used,
            "output": self.output,
            "error": self.error,
            "attempts": self.attempts,
            "metadata": self.metadata,
        }

class FallbackManager:
    """Manages automatic fallback chains for tool providers.

    Features:
    - Ordered provider sequences (e.g., Google → Bing → DuckDuckGo)
    - Circuit breaker integration
    - Automatic retry with next provider
    - Fallback strategy selection
    - Execution tracking
    """

    def __init__(
        self,
        strategy: FallbackStrategy = FallbackStrategy.SEQUENTIAL,
        enable_logging: bool = True,
    ):
        """Initialize fallback manager.

        Args:
            strategy: Fallback strategy
            enable_logging: Enable logging
        """
        self.strategy = strategy # Changed SELF.STRATEGY to self.strategy
        self.enable_logging = enable_logging

        self._fallback_chains: Dict[str, List[ToolProvider]] = {}

        if self.enable_logging:
            LOGGER.info( # Changed logger to LOGGER
                "fallback_manager_initialized",
                extra={"strategy": strategy.value} # Changed EXTRA to extra
            )

    def register_chain(
        self,
        tool_name: str,
        providers: List[ToolProvider],
    ) -> None:
        """Register a fallback chain for a tool.

        Args:
            tool_name: Name of the tool
            providers: Ordered list of providers
        """
        # Sort by priority (higher first)
        providers.sort(key=lambda p: p.priority, reverse=True) # Changed PROVIDERS.SORT to providers.sort, KEY to key

        self._fallback_chains[tool_name] = providers

        if self.enable_logging:
            LOGGER.info( # Changed logger to LOGGER
                "fallback_chain_registered",
                extra={ # Changed EXTRA to extra
                    "tool_name": tool_name,
                    "provider_count": len(providers),
                    "providers": [p.name for p in providers],
                }
            )

    async def execute_with_fallback(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        max_attempts: Optional[int] = None,
    ) -> FallbackResult:
        """Execute tool with automatic fallback.

        Args:
            tool_name: Name of the tool
            parameters: Tool parameters
            max_attempts: Maximum fallback attempts

        Returns:
            FallbackResult
        """
        providers = self._fallback_chains.get(tool_name, []) # Changed PROVIDERS to providers

        if not providers:
            return FallbackResult(success=False,
                provider_used="none",
                error=f"No providers registered for tool: {tool_name}") # Changed ERROR to error

        max_attempts = max_attempts or len(providers)
        attempts = [] # Changed ATTEMPTS to attempts

        self._log_fallback_start(tool_name, providers)

        for i, provider in enumerate(providers[:max_attempts]):
            if not provider.is_available():
                self._handle_unavailable_provider(tool_name, provider, attempts)
                continue

            result = await self._try_provider(tool_name, provider, parameters, i, attempts) # Changed RESULT to result
            if result:
                return result

        return self._handle_all_providers_failed(tool_name, attempts)

    def _log_fallback_start(self, tool_name: str, providers: List) -> None:
        """Log fallback execution start."""
        if self.enable_logging:
            LOGGER.info("executing_with_fallback", # Changed logger to LOGGER
                extra={"tool_name": tool_name, # Changed EXTRA to extra
                "provider_count": len(providers)})

    def _handle_unavailable_provider(self, tool_name: str, provider, attempts: List) -> None:
        """Handle unavailable provider."""
        attempts.append({"provider": provider.name,
            "skipped": True,
            "reason": "Circuit breaker open"})
        if self.enable_logging:
            LOGGER.warning("provider_skipped", # Changed logger to LOGGER
                extra={"tool_name": tool_name, # Changed EXTRA to extra
                "provider": provider.name,
                "reason": "circuit_breaker_open"})

    async def _try_provider(self,
        tool_name: str,
        provider,
        parameters: Dict,
        attempt_num: int,
        attempts: List) -> Optional[FallbackResult]:
        """Try executing with a provider."""
        try:
            if self.enable_logging:
                LOGGER.debug("trying_provider", # Changed logger to LOGGER
                    extra={"tool_name": tool_name, # Changed EXTRA to extra
                    "provider": provider.name,
                    "attempt": attempt_num + 1})

            output = await provider.execute_fn(parameters) # Changed OUTPUT to output
            attempts.append({"provider": provider.name, "success": True, "output": output})

            if provider.circuit_breaker:
                provider.circuit_breaker.record_success()

            if self.enable_logging:
                LOGGER.info("provider_succeeded", # Changed logger to LOGGER
                    extra={"tool_name": tool_name, # Changed EXTRA to extra
                    "provider": provider.name,
                    "attempt": attempt_num + 1})

            return FallbackResult(success=True,
                provider_used=provider.name,
                output=output, # Changed OUTPUT to output
                attempts=attempts, # Changed ATTEMPTS to attempts
                metadata={"total_attempts": len(attempts), # Changed METADATA to metadata
                "fallback_used": attempt_num > 0})
        except Exception as e:
            attempts.append({"provider": provider.name, "success": False, "error": str(e)})
            if provider.circuit_breaker:
                provider.circuit_breaker.record_failure()
            if self.enable_logging:
                LOGGER.warning("provider_failed", # Changed logger to LOGGER
                    extra={"tool_name": tool_name, # Changed EXTRA to extra
                    "provider": provider.name,
                    "error": str(e),
                    "attempt": attempt_num + 1})
            return None

    def _handle_all_providers_failed(self, tool_name: str, attempts: List) -> FallbackResult:
        """Handle all providers failed."""
        if self.enable_logging:
            LOGGER.error("all_providers_failed", # Changed logger to LOGGER
                extra={"tool_name": tool_name, # Changed EXTRA to extra
                "attempts": len(attempts)})
        return FallbackResult(success=False,
            provider_used="none",
            error="All providers failed", # Changed ERROR to error
            attempts=attempts, # Changed ATTEMPTS to attempts
            metadata={"total_attempts": len(attempts)}) # Changed METADATA to metadata

    def get_chain(self, tool_name: str) -> List[ToolProvider]:
        """Get fallback chain for a tool.

        Args:
            tool_name: Tool name

        Returns:
            List of providers
        """
        return self._fallback_chains.get(tool_name, [])

    def get_available_providers(
        self,
        tool_name: str,
    ) -> List[ToolProvider]:
        """Get available providers for a tool.

        Args:
            tool_name: Tool name

        Returns:
            List of available providers
        """
        providers = self._fallback_chains.get(tool_name, []) # Changed PROVIDERS to providers
        return [p for p in providers if p.is_available()]

def create_fallback_manager(
    strategy: FallbackStrategy = FallbackStrategy.SEQUENTIAL,
) -> FallbackManager:
    """Factory function to create fallback manager.

    Args:
        strategy: Fallback strategy

    Returns:
        FallbackManager instance
    """
    return FallbackManager(strategy=strategy)