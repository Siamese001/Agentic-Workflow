"""
HardenedLiteLLMRouter - Resilient provider switching with circuit breaking.

Implements priority-failover graph for LLM providers with automatic failover,
circuit breaking at the provider level, and real-time health monitoring.
"""

import time
import logging
from typing import Any, Dict, List, Optional
from enum import Enum

from pydantic import BaseModel, Field

from .circuit_breaker import CircuitBreaker, CircuitBreakerError
from .telemetry import get_telemetry

logger = logging.getLogger(__name__)


class ProviderType(str, Enum):
    """Supported LLM provider types."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    AZURE = "azure"
    MISTRAL = "mistral"
    COHERE = "cohere"
    GROQ = "groq"
    TOGETHER = "together"
    FIREWORKS = "fireworks"


class ProviderConfig(BaseModel):
    """Configuration for a single LLM provider endpoint."""
    provider_name: ProviderType
    model_id: str = Field(..., description="The specific model tag (e.g., 'gpt-4o', 'claude-3-opus').")
    
    # Routing Weights
    priority_rank: int = Field(1, description="1 = Primary, 2 = Secondary, etc.")
    latency_weight: float = Field(1.0, description="Preference weight for weighted routing.")
    
    # Resilience Settings
    timeout_seconds: int = Field(30, description="Strict timeout for this specific provider.")
    max_failures: int = Field(5, description="Failures before circuit opens.")
    circuit_break_duration: int = Field(60, description="Seconds to keep provider blacklisted after failure.")
    
    # Optional API configuration
    api_key: Optional[str] = None
    api_base: Optional[str] = None


class CircuitOpenError(Exception):
    """Raised when a specific provider is currently blacklisted."""
    pass


class AllProvidersFailedError(Exception):
    """Raised when no healthy providers remain."""
    pass


class HardenedLiteLLMRouter:
    """
    Military-grade router for LLM traffic.
    
    Features:
    - Priority-based failover graph
    - Provider-level circuit breaking
    - Automatic health monitoring
    - Weighted routing support
    - Real-time provider blacklisting
    """
    
    def __init__(self, providers: List[ProviderConfig]):
        """Initialize hardened router.
        
        Args:
            providers: List of provider configurations
        """
        # Sort by priority rank (1 = highest priority)
        self.providers = sorted(providers, key=lambda p: p.priority_rank)
        
        # Initialize circuit breakers for each provider
        self._circuit_breakers: Dict[str, CircuitBreaker] = {
            p.provider_name.value: CircuitBreaker(
                name=f"provider_{p.provider_name.value}",
                fail_max=p.max_failures,
                reset_timeout=p.circuit_break_duration
            )
            for p in self.providers
        }
        
        # Telemetry
        self.telemetry = get_telemetry()
        
        # Statistics
        self._provider_stats: Dict[str, Dict[str, Any]] = {
            p.provider_name.value: {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_latency_ms": 0.0,
                "avg_latency_ms": 0.0
            }
            for p in self.providers
        }
        
        logger.info(
            f"HardenedLiteLLMRouter initialized with {len(self.providers)} providers: "
            f"{[p.provider_name.value for p in self.providers]}"
        )
    
    def _check_circuit(self, provider: ProviderConfig) -> bool:
        """Check if provider circuit is healthy.
        
        Args:
            provider: Provider configuration
            
        Returns:
            True if provider is healthy (circuit closed)
        """
        circuit = self._circuit_breakers[provider.provider_name.value]
        
        if circuit.is_open():
            # Check if we should attempt reset
            if circuit._should_attempt_reset():
                logger.info(
                    f"🔄 Circuit Half-Open: Retrying {provider.provider_name.value}"
                )
                return True
            return False
        
        return True
    
    def _record_failure(self, provider: ProviderConfig, error: Exception) -> None:
        """Record provider failure and update circuit breaker.
        
        Args:
            provider: Provider configuration
            error: Exception that occurred
        """
        provider_name = provider.provider_name.value
        
        # Update circuit breaker
        circuit = self._circuit_breakers[provider_name]
        circuit.record_failure()
        
        # Update statistics
        stats = self._provider_stats[provider_name]
        stats["total_requests"] += 1
        stats["failed_requests"] += 1
        
        # Log failure
        logger.warning(
            f"⚠️ Provider {provider_name} failed: {str(error)}"
        )
        
        # Check if circuit tripped
        if circuit.is_open():
            logger.error(
                f"🔥 CIRCUIT TRIPPED: {provider_name} is now blacklisted "
                f"for {provider.circuit_break_duration}s"
            )
    
    def _record_success(
        self,
        provider: ProviderConfig,
        latency_ms: float
    ) -> None:
        """Record provider success and update metrics.
        
        Args:
            provider: Provider configuration
            latency_ms: Request latency in milliseconds
        """
        provider_name = provider.provider_name.value
        
        # Update circuit breaker
        circuit = self._circuit_breakers[provider_name]
        circuit.record_success()
        
        # Update statistics
        stats = self._provider_stats[provider_name]
        stats["total_requests"] += 1
        stats["successful_requests"] += 1
        stats["total_latency_ms"] += latency_ms
        
        # Calculate average latency
        if stats["total_requests"] > 0:
            stats["avg_latency_ms"] = (
                stats["total_latency_ms"] / stats["total_requests"]
            )
        
        logger.debug(
            f"✓ Provider {provider_name} succeeded in {latency_ms:.2f}ms"
        )
    
    async def completion(
        self,
        messages: List[Dict],
        **kwargs
    ) -> Any:
        """Route completion request to best available provider.
        
        Iterates through priority list until success or total exhaustion.
        
        Args:
            messages: List of message dictionaries
            **kwargs: Additional arguments for completion
            
        Returns:
            Completion response
            
        Raises:
            AllProvidersFailedError: If all providers fail
        """
        last_error = None
        attempted_providers = []
        
        for provider in self.providers:
            # 1. Circuit Check
            if not self._check_circuit(provider):
                logger.debug(
                    f"Skipping {provider.provider_name.value} (circuit open)"
                )
                continue
            
            attempted_providers.append(provider.provider_name.value)
            
            # 2. Attempt Execution
            start_time = time.time()
            
            try:
                logger.info(
                    f"Attempting route: {provider.provider_name.value} "
                    f"({provider.model_id})"
                )
                
                # Import litellm here to avoid circular dependencies
                import litellm
                
                # Execute completion with provider-specific timeout
                response = await litellm.acompletion(
                    model=provider.model_id,
                    messages=messages,
                    timeout=provider.timeout_seconds,
                    api_key=provider.api_key,
                    api_base=provider.api_base,
                    **kwargs
                )
                
                # Calculate latency
                latency_ms = (time.time() - start_time) * 1000
                
                # Record success
                self._record_success(provider, latency_ms)
                
                # Log telemetry
                if self.telemetry:
                    self.telemetry.log_operation(
                        component="HardenedLiteLLMRouter",
                        operation=f"completion_{provider.provider_name.value}",
                        duration=latency_ms / 1000,
                        tokens=response.usage.total_tokens if hasattr(response, 'usage') else 0
                    )
                
                logger.info(
                    f"✅ Completion successful via {provider.provider_name.value} "
                    f"in {latency_ms:.2f}ms"
                )
                
                return response
                
            except Exception as e:
                # Record failure
                self._record_failure(provider, e)
                last_error = e
                
                # Log telemetry
                if self.telemetry:
                    self.telemetry.log_operation(
                        component="HardenedLiteLLMRouter",
                        operation=f"completion_{provider.provider_name.value}",
                        duration=(time.time() - start_time),
                        error=str(e)
                    )
                
                # Continue to next provider
                continue
        
        # If loop finishes without returning, all providers failed
        raise AllProvidersFailedError(
            f"CRITICAL: All providers failed. "
            f"Attempted: {attempted_providers}. "
            f"Last error: {last_error}"
        )
    
    def get_provider_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health status of all providers.
        
        Returns:
            Dictionary mapping provider names to health status
        """
        health = {}
        
        for provider in self.providers:
            provider_name = provider.provider_name.value
            circuit = self._circuit_breakers[provider_name]
            stats = self._provider_stats[provider_name]
            
            health[provider_name] = {
                "provider": provider_name,
                "model": provider.model_id,
                "priority_rank": provider.priority_rank,
                "circuit_state": circuit.state.value,
                "healthy": circuit.is_closed(),
                "statistics": stats,
                "circuit_stats": circuit.stats.to_dict() if hasattr(circuit.stats, 'to_dict') else {}
            }
        
        return health
    
    def get_available_providers(self) -> List[str]:
        """Get list of currently available (healthy) providers.
        
        Returns:
            List of provider names with closed circuits
        """
        available = []
        
        for provider in self.providers:
            if self._check_circuit(provider):
                available.append(provider.provider_name.value)
        
        return available
    
    def reset_provider_circuit(self, provider_name: str) -> None:
        """Manually reset a provider's circuit breaker.
        
        Args:
            provider_name: Provider name to reset
        """
        if provider_name in self._circuit_breakers:
            self._circuit_breakers[provider_name].reset()
            logger.info(f"Manually reset circuit for provider: {provider_name}")
        else:
            logger.warning(f"Unknown provider: {provider_name}")
    
    def reset_all_circuits(self) -> None:
        """Reset all provider circuit breakers."""
        for circuit in self._circuit_breakers.values():
            circuit.reset()
        logger.info("All provider circuits manually reset")


def create_default_router() -> HardenedLiteLLMRouter:
    """Create a router with default provider configuration.
    
    Returns:
        HardenedLiteLLMRouter with standard providers
    """
    providers = [
        # Primary: OpenAI (GPT-4o)
        ProviderConfig(
            provider_name=ProviderType.OPENAI,
            model_id="gpt-4o",
            priority_rank=1,
            max_failures=3,
            timeout_seconds=30
        ),
        # Secondary: Anthropic (Claude 3.5 Sonnet)
        ProviderConfig(
            provider_name=ProviderType.ANTHROPIC,
            model_id="claude-3-5-sonnet-20240620",
            priority_rank=2,
            max_failures=3,
            timeout_seconds=30
        ),
        # Tertiary: Google (Gemini 1.5 Pro)
        ProviderConfig(
            provider_name=ProviderType.GOOGLE,
            model_id="gemini-1.5-pro",
            priority_rank=3,
            max_failures=5,
            timeout_seconds=30
        )
    ]
    
    return HardenedLiteLLMRouter(providers)
