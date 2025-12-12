"""Resilience components for error recovery and circuit breaking."""

from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerState,
    CircuitBreakerOpenError,
    get_breaker,
)
from .error_recovery import (
    ErrorRecoveryManager,
    RecoveryStrategy,
    ResilienceError,
    TransientError,
    PermanentError,
    RetryExhaustedError,
)
from .rate_limiter import (
    RateLimiter,
    TokenBucket,
    FixedWindow,
    RateLimitExceeded,
)
from .backoff import (
    BackoffStrategy,
    ExponentialBackoff,
    LinearBackoff,
    calculate_backoff_ms,
)
from .telemetry import (
    SystemTelemetry,
    TelemetryEvent,
    OperationStatus,
    get_telemetry,
    set_telemetry,
)
from .mixin import (
    HardeningMixin,
    TokenLimitError,
)

__all__ = [
    "CircuitBreaker",
    "CircuitBreakerState",
    "CircuitBreakerOpenError",
    "get_breaker",
    "ErrorRecoveryManager",
    "RecoveryStrategy",
    "ResilienceError",
    "TransientError",
    "PermanentError",
    "RetryExhaustedError",
    "RateLimiter",
    "TokenBucket",
    "FixedWindow",
    "RateLimitExceeded",
    "BackoffStrategy",
    "ExponentialBackoff",
    "LinearBackoff",
    "calculate_backoff_ms",
    "SystemTelemetry",
    "TelemetryEvent",
    "OperationStatus",
    "get_telemetry",
    "set_telemetry",
    "HardeningMixin",
    "TokenLimitError",
]
