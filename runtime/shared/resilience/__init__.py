"""
Unified Hardening Infrastructure - Resilience patterns for the Windsurf architecture.

This module provides military-grade resilience patterns including:
- Circuit Breaking: Prevents cascading failures
- Retry Logic: Handles transient errors with exponential backoff
- Telemetry: Structured logging and metrics
- Atomic State Management: ACID transactions for workflow state
- Provider Routing: Intelligent failover with health monitoring

Usage:
    from runtime.shared.resilience import (
        HardeningMixin,
        HardeningConfig,
        AtomicStateManager,
        HardenedLiteLLMRouter,
        CircuitBreaker,
        get_telemetry
    )
"""

from .circuit_breaker import CircuitBreaker, CircuitBreakerError, CircuitState
from .telemetry import SystemTelemetry, get_telemetry, OperationMetrics
from .hardening_mixin import HardeningMixin, HardeningConfig
from .atomic_state_manager import (
    AtomicStateManager,
    WorkflowState,
    StateCorruptionError,
    StateLockError,
    execute_and_checkpoint
)
from .hardened_litellm_router import (
    HardenedLiteLLMRouter,
    ProviderConfig,
    ProviderType,
    AllProvidersFailedError,
    create_default_router
)

__all__ = [
    # Circuit Breaking
    "CircuitBreaker",
    "CircuitBreakerError",
    "CircuitState",

    # Telemetry
    "SystemTelemetry",
    "get_telemetry",
    "OperationMetrics",

    # Hardening Mixin
    "HardeningMixin",
    "HardeningConfig",

    # Atomic State Management
    "AtomicStateManager",
    "WorkflowState",
    "StateCorruptionError",
    "StateLockError",
    "execute_and_checkpoint",

    # LiteLLM Router
    "HardenedLiteLLMRouter",
    "ProviderConfig",
    "ProviderType",
    "AllProvidersFailedError",
    "create_default_router",
]
