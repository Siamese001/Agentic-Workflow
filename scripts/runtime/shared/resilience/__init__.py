"""

logger = logging.getLogger(__name__)
Unified Hardening Infrastructure - Resilience patterns for the Windsurf architecture.

This module provides military-grade resilience patterns including:
- Circuit Breaking: Prevents cascading failures
- Retry Logic: Handles transient errors with exponential backoff
- Telemetry: Structured logging and metrics
- Atomic State Management: ACID transactions for workflow state
- Provider Routing: Intelligent failover with health monitoring

Usage:
        HardeningMixin,
        HardeningConfig,
        AtomicStateManager,
        HardenedLiteLLMRouter,
        CircuitBreaker,
        get_telemetry
    )
"""
import logging

    AtomicStateManager,
    WorkflowState,
    StateCorruptionError,
    StateLockError,
    execute_and_checkpoint
)
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
