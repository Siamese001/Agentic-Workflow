"""Behavioral tests for ``agentic_core.L5_safety.enforcement.circuit_breaker_gate``.

Covers:
- CircuitState / config / metrics dataclass defaults.
- CircuitBreakerOpenError / CircuitBreakerTimeoutError carry metadata.
- CLOSED → OPEN transition after N failures; rejects while open.
- OPEN → HALF_OPEN after reset_timeout; allow limited calls.
- HALF_OPEN success_threshold → CLOSED; failure → exponential backoff + OPEN.
- CLOSED success resets failure_count.
- Metrics accumulate correctly (total/success/fail/rejected/state transitions).
- get_time_until_retry returns 0 when not OPEN, remaining otherwise.
- protect(): passes result through when CLOSED; raises OpenError when OPEN.
- Singleton registry: get_breaker caches by name; reset_registry clears it.
"""

from __future__ import annotations

import time
from collections.abc import Generator
from unittest.mock import patch  # noqa: F401

import pytest

from agentic_core.L5_safety.enforcement import circuit_breaker_gate as mod
from agentic_core.L5_safety.enforcement.circuit_breaker_gate import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitBreakerMetrics,
    CircuitBreakerOpenError,
    CircuitBreakerTimeoutError,
    CircuitState,
    get_all_breakers,
    get_breaker,
    reset_registry,
)


@pytest.fixture(autouse=True)
def _clean_registry() -> Generator[None, None, None]:
    reset_registry()
    yield
    reset_registry()


# ---- Dataclass defaults + enum ------------------------------------------

class TestDefaults:
    def test_circuit_state_values(self) -> None:
        assert CircuitState.CLOSED.value == "closed"
        assert CircuitState.OPEN.value == "open"
        assert CircuitState.HALF_OPEN.value == "half_open"

    def test_config_defaults(self) -> None:
        c = CircuitBreakerConfig()
        assert c.failure_threshold == 5
        assert c.success_threshold == 2
        assert c.reset_timeout_seconds == 60.0
        assert c.max_reset_timeout_seconds == 600.0
        assert c.backoff_multiplier == 2.0
        assert c.half_open_max_calls == 3
        assert c.execution_timeout_seconds == 30.0

    def test_metrics_defaults(self) -> None:
        m = CircuitBreakerMetrics()
        assert m.total_calls == 0
        assert m.successful_calls == 0
        assert m.failed_calls == 0
        assert m.rejected_calls == 0
        assert m.timed_out_calls == 0
        assert m.state_transitions == 0
        assert m.last_failure_time is None
        assert m.current_backoff == 0.0


# ---- Exceptions ----------------------------------------------------------

class TestExceptions:
    def test_open_error_carries_metadata(self) -> None:
        e = CircuitBreakerOpenError("svc", 12.3)
        assert e.breaker_name == "svc"
        assert e.time_until_retry == 12.3
        assert "svc" in str(e)
        assert "12.3" in str(e)

    def test_timeout_error_carries_metadata(self) -> None:
        e = CircuitBreakerTimeoutError("svc", 5.0)
        assert e.breaker_name == "svc"
        assert e.timeout == 5.0
        assert "svc" in str(e)


# ---- State transitions --------------------------------------------------

class TestStateTransitions:
    def test_starts_closed(self) -> None:
        cb = CircuitBreaker("t")
        assert cb.is_closed
        assert not cb.is_open
        assert not cb.is_half_open

    def test_closed_allows_requests(self) -> None:
        cb = CircuitBreaker("t")
        assert cb.allow_request() is True
        assert cb.metrics.total_calls == 1

    def test_closed_to_open_after_threshold(self) -> None:
        cb = CircuitBreaker("t", CircuitBreakerConfig(failure_threshold=3))
        for _ in range(3):
            cb.record_failure(RuntimeError("x"))
        assert cb.is_open
        assert cb.metrics.failed_calls == 3
        assert cb.metrics.state_transitions >= 1

    def test_below_threshold_stays_closed(self) -> None:
        cb = CircuitBreaker("t", CircuitBreakerConfig(failure_threshold=5))
        for _ in range(4):
            cb.record_failure()
        assert cb.is_closed

    def test_closed_success_resets_failure_count(self) -> None:
        cb = CircuitBreaker("t", CircuitBreakerConfig(failure_threshold=3))
        cb.record_failure()
        cb.record_failure()
        cb.record_success()
        # Next 2 failures should not trip; we have 0 again
        cb.record_failure()
        cb.record_failure()
        assert cb.is_closed

    def test_open_rejects_until_reset_timeout(self) -> None:
        cb = CircuitBreaker("t", CircuitBreakerConfig(
            failure_threshold=1, reset_timeout_seconds=60.0,
        ))
        cb.record_failure()
        assert cb.is_open
        # Next allow_request stays rejected
        assert cb.allow_request() is False
        assert cb.metrics.rejected_calls == 1

    def test_open_to_half_open_after_timeout(self) -> None:
        cb = CircuitBreaker("t", CircuitBreakerConfig(
            failure_threshold=1, reset_timeout_seconds=0.01,
        ))
        cb.record_failure()
        assert cb.is_open
        time.sleep(0.02)
        assert cb.allow_request() is True
        assert cb.is_half_open

    def test_half_open_caps_concurrent_calls(self) -> None:
        cb = CircuitBreaker("t", CircuitBreakerConfig(
            failure_threshold=1, reset_timeout_seconds=0.01, half_open_max_calls=2,
        ))
        cb.record_failure()
        time.sleep(0.02)
        # First call transitions OPEN→HALF_OPEN and returns True WITHOUT bumping
        # _half_open_calls. Subsequent HALF_OPEN calls bump the counter up to
        # half_open_max_calls, after which they are rejected.
        assert cb.allow_request() is True   # transitional, count stays 0
        assert cb.allow_request() is True   # count -> 1
        assert cb.allow_request() is True   # count -> 2
        assert cb.allow_request() is False  # capped

    def test_half_open_to_closed_after_success_threshold(self) -> None:
        cb = CircuitBreaker("t", CircuitBreakerConfig(
            failure_threshold=1, reset_timeout_seconds=0.01,
            success_threshold=2, half_open_max_calls=5,
        ))
        cb.record_failure()
        time.sleep(0.02)
        cb.allow_request()
        cb.record_success()
        cb.allow_request()
        cb.record_success()
        assert cb.is_closed

    def test_half_open_failure_reopens_with_backoff(self) -> None:
        cfg = CircuitBreakerConfig(
            failure_threshold=1, reset_timeout_seconds=1.0,
            backoff_multiplier=2.0, max_reset_timeout_seconds=60.0,
        )
        cb = CircuitBreaker("t", cfg)
        cb.record_failure()
        # Manually flip to half_open by resetting last failure and allowing
        cb._last_failure_time = time.time() - 2.0  # type: ignore[attr-defined]
        cb.allow_request()  # triggers half_open transition
        assert cb.is_half_open
        cb.record_failure(RuntimeError("still broken"))
        assert cb.is_open
        assert cb._current_reset_timeout >= 2.0  # doubled  # type: ignore[attr-defined]
        assert cb.metrics.current_backoff >= 2.0


# ---- Metrics -------------------------------------------------------------

class TestMetrics:
    def test_timeout_error_bumps_timed_out_counter(self) -> None:
        cb = CircuitBreaker("t")
        cb.record_failure(CircuitBreakerTimeoutError("t", 5.0))
        assert cb.metrics.timed_out_calls == 1
        assert cb.metrics.failed_calls == 1

    def test_success_tracks_last_success_time(self) -> None:
        cb = CircuitBreaker("t")
        cb.record_success()
        assert cb.metrics.last_success_time is not None
        assert cb.metrics.successful_calls == 1


# ---- get_time_until_retry -----------------------------------------------

class TestTimeUntilRetry:
    def test_zero_when_closed(self) -> None:
        cb = CircuitBreaker("t")
        assert cb.get_time_until_retry() == 0.0

    def test_zero_when_no_failure_recorded(self) -> None:
        cb = CircuitBreaker("t")
        cb._state = CircuitState.OPEN  # type: ignore[attr-defined]
        assert cb.get_time_until_retry() == 0.0

    def test_positive_when_open_recent_failure(self) -> None:
        cb = CircuitBreaker("t", CircuitBreakerConfig(
            failure_threshold=1, reset_timeout_seconds=60.0,
        ))
        cb.record_failure()
        remaining = cb.get_time_until_retry()
        assert 0.0 < remaining <= 60.0

    def test_zero_after_timeout_elapsed(self) -> None:
        cb = CircuitBreaker("t", CircuitBreakerConfig(
            failure_threshold=1, reset_timeout_seconds=0.01,
        ))
        cb.record_failure()
        time.sleep(0.02)
        assert cb.get_time_until_retry() == 0.0


# ---- protect() decorator ------------------------------------------------

class TestProtect:
    def test_passes_result_when_closed(self) -> None:
        cb = CircuitBreaker("t", CircuitBreakerConfig(execution_timeout_seconds=5.0))
        wrapped = cb.protect(lambda x: x * 2)
        assert wrapped(21) == 42
        assert cb.metrics.successful_calls >= 1

    def test_raises_open_error_when_open(self) -> None:
        cb = CircuitBreaker("t", CircuitBreakerConfig(
            failure_threshold=1, reset_timeout_seconds=60.0,
            execution_timeout_seconds=5.0,
        ))
        cb.record_failure()
        wrapped = cb.protect(lambda: 1)
        with pytest.raises(CircuitBreakerOpenError):
            wrapped()

    def test_preserves_function_name(self) -> None:
        cb = CircuitBreaker("t")
        def original() -> int:
            return 1
        wrapped = cb.protect(original)
        assert wrapped.__name__ == "original"


# ---- Registry -----------------------------------------------------------

class TestRegistry:
    def test_get_breaker_caches_by_name(self) -> None:
        a = get_breaker("svc")
        b = get_breaker("svc")
        assert a is b

    def test_different_names_different_instances(self) -> None:
        a = get_breaker("x")
        b = get_breaker("y")
        assert a is not b
        assert a.name == "x"
        assert b.name == "y"

    def test_get_breaker_passes_kwargs_to_config(self) -> None:
        cb = get_breaker("svc", failure_threshold=99)
        assert cb.config.failure_threshold == 99

    def test_get_all_breakers_snapshot(self) -> None:
        get_breaker("a")
        get_breaker("b")
        all_br = get_all_breakers()
        assert set(all_br.keys()) == {"a", "b"}
        # Returns a copy — mutating it doesn't affect internal registry
        all_br.clear()
        assert set(get_all_breakers().keys()) == {"a", "b"}

    def test_reset_registry_clears(self) -> None:
        get_breaker("x")
        assert len(get_all_breakers()) == 1
        reset_registry()
        assert len(get_all_breakers()) == 0
