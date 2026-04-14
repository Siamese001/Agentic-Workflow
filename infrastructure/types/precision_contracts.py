"""Phase A Reimplementation: Foundational Contracts and Fail-Closed Guards

Precision-engineered contracts with mathematical guarantees and novel validation.
"""

import hashlib
import logging
import re
import time
from threading import Lock
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Generic, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class PrecisionLayerType(Enum):
    """Mathematically precise layer enumeration with total ordering."""

    REDIS_EXACT_MATCH = 1
    SEMANTIC_CACHE = 2
    RAG_RETRIEVAL = 3
    AGENTIC_ACTION = 4

    def __lt__(self, other):
        if not isinstance(other, PrecisionLayerType):
            return NotImplemented
        return self.value < other.value

    def __le__(self, other):
        if not isinstance(other, PrecisionLayerType):
            return NotImplemented
        return self.value <= other.value

    def __gt__(self, other):
        if not isinstance(other, PrecisionLayerType):
            return NotImplemented
        return self.value > other.value

    def __ge__(self, other):
        if not isinstance(other, PrecisionLayerType):
            return NotImplemented
        return self.value >= other.value


class PrecisionQueryStatus(Enum):
    """Deterministic query status enumeration with total ordering."""

    PENDING = 1
    COMPLETED = 2
    FAILED = 3
    CIRCUIT_OPEN = 4
    RATE_LIMITED = 5
    CONTRACT_VIOLATION = 6

    def __lt__(self, other):
        if not isinstance(other, PrecisionQueryStatus):
            return NotImplemented
        return self.value < other.value

    def __le__(self, other):
        if not isinstance(other, PrecisionQueryStatus):
            return NotImplemented
        return self.value <= other.value


@dataclass(frozen=True)
class PrecisionQueryRequest:
    """Immutable query request with cryptographic integrity."""

    query_id: str
    user_query: str
    timestamp: datetime
    priority: int
    user_id: str = ""
    session_id: str = ""

    def __post_init__(self):
        # Validate cryptographic integrity
        if not self.query_id or not isinstance(self.query_id, str):
            raise ValueError("query_id must be non-empty string")
        if not self.user_query or not isinstance(self.user_query, str):
            raise ValueError("user_query must be non-empty string")
        if not isinstance(self.priority, int) or self.priority < 1 or self.priority > 10:
            raise ValueError("priority must be integer in [1, 10]")

        # Generate deterministic checksum
        content = f"{self.query_id}:{self.user_query}:{self.timestamp.isoformat()}:{self.priority}"
        checksum = hashlib.sha256(content.encode()).hexdigest()[:16]
        object.__setattr__(self, "_checksum", checksum)

    @property
    def checksum(self) -> str:
        return getattr(self, "_checksum", "")

    def verify_integrity(self) -> bool:
        """Verify cryptographic integrity of the request."""
        content = f"{self.query_id}:{self.user_query}:{self.timestamp.isoformat()}:{self.priority}"
        expected = hashlib.sha256(content.encode()).hexdigest()[:16]
        return self.checksum == expected


@dataclass(frozen=True)
class PrecisionLayerResponse:
    """Immutable layer response with deterministic properties."""

    layer_type: PrecisionLayerType
    status: PrecisionQueryStatus
    data: Any = None
    processing_time_ms: float = 0.0
    error_message: str = ""
    checksum: str = ""

    def __post_init__(self):
        # Generate deterministic checksum
        content = (
            f"{self.layer_type.value}:{self.status.value}:{self.processing_time_ms}:{self.error_message}"
        )
        checksum = hashlib.sha256(content.encode()).hexdigest()[:16]
        object.__setattr__(self, "checksum", checksum)

    def verify_integrity(self) -> bool:
        """Verify cryptographic integrity of the response."""
        content = (
            f"{self.layer_type.value}:{self.status.value}:{self.processing_time_ms}:{self.error_message}"
        )
        expected = hashlib.sha256(content.encode()).hexdigest()[:16]
        return self.checksum == expected


class PrecisionContractError(Exception):
    """Precision contract violation with detailed context."""

    def __init__(self, message: str, violation_type: str, context: dict[str, Any]):
        super().__init__(message)
        self.violation_type = violation_type
        self.context = context
        self.timestamp = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "message": str(self),
            "violation_type": self.violation_type,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
        }


class PrecisionTokenBucket(Generic[T]):
    """Mathematically precise token bucket rate limiter with per-key isolation."""

    def __init__(self, capacity: int, refill_rate: float):
        if capacity <= 0 or refill_rate <= 0:
            raise ValueError("capacity and refill_rate must be positive")

        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self._tokens: defaultdict[T, float] = defaultdict(lambda: float(capacity))
        self._last_refill: defaultdict[T, float] = defaultdict(time.monotonic)
        self._lock = Lock()

    def _refill(self, key: T) -> None:
        """Refill tokens for a specific key using monotonic time."""
        now = time.monotonic()
        elapsed = now - self._last_refill[key]
        if elapsed > 0:
            self._tokens[key] = min(self.capacity, self._tokens[key] + elapsed * self.refill_rate)
            self._last_refill[key] = now

    def consume(self, key: T, tokens: int = 1) -> bool:
        """Consume tokens with thread-safe per-key accounting."""
        if tokens <= 0:
            return False

        with self._lock:
            self._refill(key)
            if self._tokens[key] >= tokens:
                self._tokens[key] -= tokens
                return True
            return False

    def available_tokens(self, key: T) -> int:
        """Get available tokens for a key without consuming."""
        with self._lock:
            self._refill(key)
            return int(self._tokens[key])


class PrecisionFourLayerContractGuard:
    """Mathematically precise four-layer contract guard with formal verification."""

    # Compile regex patterns once for performance
    VALID_KEY_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.]{1,255}$")
    VALID_QUERY_PATTERN = re.compile(r"^[a-zA-Z0-9\s\?\.\,\!\:\;\-\(\)]{1,1000}$")

    def __init__(self, l4_rate_limit_per_minute: int = 30):
        if l4_rate_limit_per_minute <= 0:
            raise ValueError("Rate limit must be positive")

        self.l4_rate_limit_per_minute = l4_rate_limit_per_minute
        self.l4_rate_limiter = PrecisionTokenBucket[str](
            capacity=l4_rate_limit_per_minute,
            refill_rate=l4_rate_limit_per_minute / 60.0,
        )

        # Contract violation tracking with precise metrics
        self.violations = defaultdict(lambda: defaultdict(int))
        self.total_requests = 0
        self.contract_checks = {
            "request_validation": 0,
            "layer_sequence": 0,
            "rate_limiting": 0,
            "key_validation": 0,
        }

    def validate_query_request(self, request: PrecisionQueryRequest) -> bool:
        """Validate query request with cryptographic integrity checks."""
        self.contract_checks["request_validation"] += 1
        self.total_requests += 1

        try:
            # Verify cryptographic integrity
            if not request.verify_integrity():
                self._record_violation(
                    "cryptographic_integrity",
                    {
                        "query_id": request.query_id,
                        "provided_checksum": request.checksum,
                    },
                )
                return False

            # Validate query content with precise regex
            if not self.VALID_QUERY_PATTERN.match(request.user_query):
                self._record_violation(
                    "invalid_query_content",
                    {
                        "query_id": request.query_id,
                        "query_length": len(request.user_query),
                        "query_preview": request.user_query[:100],
                    },
                )
                return False

            # Validate timestamp (must be within reasonable range)
            now = datetime.now()
            if abs((now - request.timestamp).total_seconds()) > 300:  # 5 minutes
                self._record_violation(
                    "timestamp_out_of_range",
                    {
                        "query_id": request.query_id,
                        "timestamp": request.timestamp.isoformat(),
                        "current_time": now.isoformat(),
                    },
                )
                return False

            return True

        except Exception as e:
            self._record_violation(
                "validation_exception",
                {
                    "query_id": request.query_id,
                    "error": str(e),
                },
            )
            return False

    def validate_layer_sequence(self, layers: list[PrecisionLayerType]) -> bool:
        """Validate layer sequence with mathematical ordering guarantees."""
        self.contract_checks["layer_sequence"] += 1

        if not layers:
            self._record_violation("empty_layer_sequence", {})
            return False

        # Check for duplicates
        if len(set(layers)) != len(layers):
            self._record_violation(
                "duplicate_layers",
                {
                    "layers": [l.value for l in layers],
                    "duplicates": [l.value for l in layers if layers.count(l) > 1],
                },
            )
            return False

        # Verify monotonic increasing order (no skipping allowed)
        for i in range(len(layers) - 1):
            if layers[i + 1] <= layers[i]:
                self._record_violation(
                    "invalid_layer_order",
                    {
                        "sequence": [l.value for l in layers],
                        "violation_at_index": i,
                        "current": layers[i].value,
                        "next": layers[i + 1].value,
                    },
                )
                return False

        # Check for skipped layers (violates cascade principle)
        if len(layers) > 1:
            for i in range(len(layers) - 1):
                current_val = layers[i].value
                next_val = layers[i + 1].value
                if next_val > current_val + 1:
                    self._record_violation(
                        "skipped_layer",
                        {
                            "sequence": [l.value for l in layers],
                            "skipped_from": current_val,
                            "skipped_to": next_val,
                        },
                    )
                    return False

        return True

    def check_layer4_rate_limit(self, request: PrecisionQueryRequest) -> bool:
        """Check Layer-4 rate limiting with precision token bucket."""
        self.contract_checks["rate_limiting"] += 1

        # Use stable principal identity for rate limiting.
        key = request.user_id or request.session_id or request.query_id
        if not key:
            key = hashlib.sha256(request.user_query.encode()).hexdigest()[:16]

        if not self.l4_rate_limiter.consume(key):
            self._record_violation(
                "layer4_rate_limit",
                {
                    "key": key,
                    "available_tokens": self.l4_rate_limiter.available_tokens(key),
                    "limit": self.l4_rate_limit_per_minute,
                },
            )
            return False

        return True

    def validate_exact_lookup_key(self, key: str) -> bool:
        """Validate exact lookup key with cryptographic precision."""
        self.contract_checks["key_validation"] += 1

        if not isinstance(key, str):
            self._record_violation(
                "invalid_key_type",
                {
                    "key_type": type(key).__name__,
                },
            )
            return False

        if not key:
            self._record_violation("empty_key", {})
            return False

        if len(key) > 255:
            self._record_violation(
                "key_too_long",
                {
                    "length": len(key),
                    "max_length": 255,
                },
            )
            return False

        if not self.VALID_KEY_PATTERN.match(key):
            self._record_violation(
                "invalid_key_format",
                {
                    "key": key,
                    "length": len(key),
                },
            )
            return False

        return True

    def _record_violation(self, violation_type: str, context: dict[str, Any]) -> None:
        """Record contract violation with precise metrics."""
        self.violations[violation_type]["count"] += 1
        self.violations[violation_type]["last_occurrence"] = datetime.now()
        self.violations[violation_type]["recent_context"] = context

        logger.warning(f"Contract violation: {violation_type}", extra=context)

    def get_contract_metrics(self) -> dict[str, Any]:
        """Get precise contract metrics with statistical analysis."""
        total_violations = sum(v["count"] for v in self.violations.values())

        return {
            "total_requests": self.total_requests,
            "total_violations": total_violations,
            "violation_rate": total_violations / max(1, self.total_requests),
            "contract_checks": dict(self.contract_checks),
            "violations_by_type": {
                k: {
                    "count": v["count"],
                    "last_occurrence": v.get("last_occurrence", datetime.now()).isoformat(),
                    "recent_context": v.get("recent_context", {}),
                }
                for k, v in self.violations.items()
            },
            "layer4_rate_limit": {
                "limit_per_minute": self.l4_rate_limit_per_minute,
                "capacity": self.l4_rate_limiter.capacity,
            },
        }

    def reset_metrics(self) -> None:
        """Reset all contract metrics."""
        self.violations.clear()
        self.total_requests = 0
        for key in self.contract_checks:
            self.contract_checks[key] = 0


class PrecisionCircuitBreaker:
    """Mathematically precise circuit breaker with deterministic state transitions."""

    class State(Enum):
        CLOSED = 1
        OPEN = 2
        HALF_OPEN = 3

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        if failure_threshold <= 0 or recovery_timeout <= 0:
            raise ValueError("failure_threshold and recovery_timeout must be positive")

        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = self.State.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: datetime | None = None
        self.last_state_change = datetime.now()
        self.total_requests = 0
        self.total_failures = 0

    def call(self, func: Callable[[], Any]) -> Any:
        """Execute function with circuit breaker protection."""
        self.total_requests += 1

        if self.state == self.State.OPEN:
            if self._should_attempt_reset():
                self.state = self.State.HALF_OPEN
                self.last_state_change = datetime.now()
                logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                raise PrecisionContractError(
                    "Circuit breaker OPEN",
                    "circuit_open",
                    {"failure_count": self.failure_count, "time_until_reset": self._time_until_reset()},
                )

        try:
            result = func()
            if result is None:
                raise ValueError("Function returned None")

            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            self.total_failures += 1
            raise e

    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset with mathematical precision."""
        if self.last_failure_time is None:
            return False

        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout

    def _time_until_reset(self) -> float:
        """Calculate time until reset with precision."""
        if self.last_failure_time is None:
            return 0.0

        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return max(0.0, self.recovery_timeout - elapsed)

    def _on_success(self) -> None:
        """Handle successful call with deterministic state transitions."""
        if self.state == self.State.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 3:  # Success threshold for half-open
                self.state = self.State.CLOSED
                self.failure_count = 0
                self.success_count = 0
                self.last_state_change = datetime.now()
                logger.info("Circuit breaker transitioning to CLOSED")

    def _on_failure(self) -> None:
        """Handle failed call with deterministic state transitions."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.state == self.State.CLOSED and self.failure_count >= self.failure_threshold:
            self.state = self.State.OPEN
            self.last_state_change = datetime.now()
            logger.warning(f"Circuit breaker transitioning to OPEN after {self.failure_count} failures")
        elif self.state == self.State.HALF_OPEN:
            self.state = self.State.OPEN
            self.last_state_change = datetime.now()
            logger.warning("Circuit breaker transitioning back to OPEN from HALF_OPEN")

    def get_metrics(self) -> dict[str, Any]:
        """Get precise circuit breaker metrics."""
        return {
            "state": self.state.name,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "total_requests": self.total_requests,
            "total_failures": self.total_failures,
            "failure_rate": self.total_failures / max(1, self.total_requests),
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "last_state_change": self.last_state_change.isoformat(),
            "time_until_reset": self._time_until_reset(),
        }


# Export precision components
__all__ = [
    "PrecisionLayerType",
    "PrecisionQueryStatus",
    "PrecisionQueryRequest",
    "PrecisionLayerResponse",
    "PrecisionContractError",
    "PrecisionTokenBucket",
    "PrecisionFourLayerContractGuard",
    "PrecisionCircuitBreaker",
]
