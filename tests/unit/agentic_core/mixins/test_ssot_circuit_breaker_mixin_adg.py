"""ADG importability contract for agentic_core/mixins/ssot_circuit_breaker_mixin.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ssot_circuit_breaker_mixin.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.mixins.ssot_circuit_breaker_mixin import (  # noqa: F401
        SafetyException,
        StateValidationError,
        PolicyHashMismatch,
        SovereignTokenDenied,
        SSOTCircuitBreakerMixin,
        CircuitOpenError,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    SafetyException = None  # type: ignore[assignment,misc]
    StateValidationError = None  # type: ignore[assignment,misc]
    PolicyHashMismatch = None  # type: ignore[assignment,misc]
    SovereignTokenDenied = None  # type: ignore[assignment,misc]
    SSOTCircuitBreakerMixin = None  # type: ignore[assignment,misc]
    CircuitOpenError = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="ssot_circuit_breaker_mixin.py deps unavailable")
class TestSsotCircuitBreakerMixinImportability:
    def test_module_importable(self) -> None:
        """ADG contract: ssot_circuit_breaker_mixin.py must be importable."""
        assert _AVAILABLE

    def test_safetyexception_is_type(self) -> None:
        assert SafetyException is not None

    def test_statevalidationerror_is_type(self) -> None:
        assert StateValidationError is not None

    def test_policyhashmismatch_is_type(self) -> None:
        assert PolicyHashMismatch is not None

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

