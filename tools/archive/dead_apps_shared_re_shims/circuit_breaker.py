"""Circuit Breaker - Re-export from enforcement for reasoning compatibility."""

from apps_shared.enforcement.circuit_breaker import (
    CircuitBreakerConfig,
    CircuitBreakerRegistry,
    get_circuit_breaker_registry,
)

__all__ = ["CircuitBreakerConfig", "CircuitBreakerRegistry", "get_circuit_breaker_registry"]
