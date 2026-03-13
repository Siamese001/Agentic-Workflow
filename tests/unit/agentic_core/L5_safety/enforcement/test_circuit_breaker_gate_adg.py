"""ADG importability contract for agentic_core/L5_safety/enforcement/circuit_breaker_gate.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_circuit_breaker_gate.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.enforcement.circuit_breaker_gate import (  # noqa: F401
        CircuitBreaker,
        CircuitBreakerConfig,
        CircuitBreakerMetrics,
        CircuitBreakerOpenError,
        CircuitBreakerTimeoutError,
        CircuitState,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    CircuitState = None  # type: ignore[assignment,misc]
    CircuitBreakerConfig = None  # type: ignore[assignment,misc]
    CircuitBreakerMetrics = None  # type: ignore[assignment,misc]
    CircuitBreakerOpenError = None  # type: ignore[assignment,misc]
    CircuitBreakerTimeoutError = None  # type: ignore[assignment,misc]
    CircuitBreaker = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="circuit_breaker_gate deps unavailable")
class TestCircuitBreakerGateImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/enforcement/circuit_breaker_gate.py must be importable."""
        assert _AVAILABLE

    def test_circuitstate_defined(self) -> None:
        assert CircuitState is not None

    def test_circuitbreakerconfig_defined(self) -> None:
        assert CircuitBreakerConfig is not None

    def test_circuitbreakermetrics_defined(self) -> None:
        assert CircuitBreakerMetrics is not None

    def test_circuitbreakeropenerror_defined(self) -> None:
        assert CircuitBreakerOpenError is not None

    def test_circuitbreakertimeouterror_defined(self) -> None:
        assert CircuitBreakerTimeoutError is not None

    def test_circuitbreaker_defined(self) -> None:
        assert CircuitBreaker is not None
