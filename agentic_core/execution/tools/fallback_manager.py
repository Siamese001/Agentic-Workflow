"""Automatic Fallback Manager for Tool Providers.

Phase 3 - Pillar 8 (Cont.): Tool Ecosystem (Automatic Fallbacks)
Implements ordered fallback chains when primary providers fail.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Awaitable

from shared.resilience import CircuitBreaker, CircuitState

logger = logging.getLogger(__name__)


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
    priority: int = 0
    circuit_breaker: Optional[CircuitBreaker] = None
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
        self.strategy = strategy
        self.enable_logging = enable_logging
        
        self._fallback_chains: Dict[str, List[ToolProvider]] = {}
        
        if self.enable_logging:
            logger.info(
                "fallback_manager_initialized",
                extra={"strategy": strategy.value}
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
        providers.sort(key=lambda p: p.priority, reverse=True)
        
        self._fallback_chains[tool_name] = providers
        
        if self.enable_logging:
            logger.info(
                "fallback_chain_registered",
                extra={
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
        providers = self._fallback_chains.get(tool_name, [])
        
        if not providers:
            return FallbackResult(
                success=False,
                provider_used="none",
                error=f"No providers registered for tool: {tool_name}",
            )
        
        max_attempts = max_attempts or len(providers)
        attempts = []
        
        if self.enable_logging:
            logger.info(
                "executing_with_fallback",
                extra={
                    "tool_name": tool_name,
                    "provider_count": len(providers),
                }
            )
        
        # Try each provider in sequence
        for i, provider in enumerate(providers[:max_attempts]):
            # Check if provider is available
            if not provider.is_available():
                attempt = {
                    "provider": provider.name,
                    "skipped": True,
                    "reason": "Circuit breaker open",
                }
                attempts.append(attempt)
                
                if self.enable_logging:
                    logger.warning(
                        "provider_skipped",
                        extra={
                            "tool_name": tool_name,
                            "provider": provider.name,
                            "reason": "circuit_breaker_open",
                        }
                    )
                continue
            
            # Try to execute
            try:
                if self.enable_logging:
                    logger.debug(
                        "trying_provider",
                        extra={
                            "tool_name": tool_name,
                            "provider": provider.name,
                            "attempt": i + 1,
                        }
                    )
                
                output = await provider.execute_fn(parameters)
                
                # Success
                attempt = {
                    "provider": provider.name,
                    "success": True,
                    "output": output,
                }
                attempts.append(attempt)
                
                # Record success in circuit breaker
                if provider.circuit_breaker:
                    provider.circuit_breaker.record_success()
                
                if self.enable_logging:
                    logger.info(
                        "provider_succeeded",
                        extra={
                            "tool_name": tool_name,
                            "provider": provider.name,
                            "attempt": i + 1,
                        }
                    )
                
                return FallbackResult(
                    success=True,
                    provider_used=provider.name,
                    output=output,
                    attempts=attempts,
                    metadata={
                        "total_attempts": len(attempts),
                        "fallback_used": i > 0,
                    }
                )
            
            except Exception as e:
                # Failure
                attempt = {
                    "provider": provider.name,
                    "success": False,
                    "error": str(e),
                }
                attempts.append(attempt)
                
                # Record failure in circuit breaker
                if provider.circuit_breaker:
                    provider.circuit_breaker.record_failure()
                
                if self.enable_logging:
                    logger.warning(
                        "provider_failed",
                        extra={
                            "tool_name": tool_name,
                            "provider": provider.name,
                            "error": str(e),
                            "attempt": i + 1,
                        }
                    )
                
                # Continue to next provider
                continue
        
        # All providers failed
        if self.enable_logging:
            logger.error(
                "all_providers_failed",
                extra={
                    "tool_name": tool_name,
                    "attempts": len(attempts),
                }
            )
        
        return FallbackResult(
            success=False,
            provider_used="none",
            error="All providers failed",
            attempts=attempts,
            metadata={
                "total_attempts": len(attempts),
            }
        )
    
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
        providers = self._fallback_chains.get(tool_name, [])
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
