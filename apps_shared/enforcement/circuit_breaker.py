"""Circuit Breaker - Stub implementation for test compatibility."""
from dataclasses import dataclass


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""
    failure_threshold: float = 0.5
    timeout: float = 30.0
    failure_rate_threshold: float = 0.5


class CircuitBreaker:
    """Stub circuit breaker."""

    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self._state = "closed"

    async def call(self, func, *args, **kwargs):
        """Call function through circuit breaker."""
        return await func(*args, **kwargs)


class CircuitBreakerRegistry:
    """Stub circuit breaker registry."""

    def __init__(self):
        self._circuit_breakers: dict[str, CircuitBreaker] = {}

    async def get_circuit_breaker(self, name: str, config: CircuitBreakerConfig | None = None) -> CircuitBreaker:
        """Get or create circuit breaker."""
        if name not in self._circuit_breakers:
            self._circuit_breakers[name] = CircuitBreaker(name, config or CircuitBreakerConfig())
        return self._circuit_breakers[name]


_registry: CircuitBreakerRegistry | None = None


async def get_circuit_breaker_registry() -> CircuitBreakerRegistry:
    """Get global circuit breaker registry."""
    global _registry
    if _registry is None:
        _registry = CircuitBreakerRegistry()
    return _registry


__all__ = ["CircuitBreakerConfig", "CircuitBreaker", "CircuitBreakerRegistry", "get_circuit_breaker_registry"]
