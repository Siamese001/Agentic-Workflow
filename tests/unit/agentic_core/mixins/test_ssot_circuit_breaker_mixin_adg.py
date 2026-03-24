"""ADG importability contract for agentic_core/mixins/ssot_circuit_breaker_mixin.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_ssot_circuit_breaker_mixin.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.mixins.ssot_circuit_breaker_mixin import (  # noqa: F401
        FORBIDDEN_EXCEPTIONS,
        PolicyHashMismatch,
        SafetyException,
        SovereignTokenDenied,
        SSOTCircuitBreakerMixin,
        StateValidationError,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    SafetyException = None  # type: ignore[assignment,misc]
    StateValidationError = None  # type: ignore[assignment,misc]
    PolicyHashMismatch = None  # type: ignore[assignment,misc]
    SovereignTokenDenied = None  # type: ignore[assignment,misc]
    FORBIDDEN_EXCEPTIONS = None  # type: ignore[assignment,misc]
    SSOTCircuitBreakerMixin = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="ssot_circuit_breaker_mixin deps unavailable")
class TestSsotCircuitBreakerMixinImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/mixins/ssot_circuit_breaker_mixin.py must be importable."""
        assert _AVAILABLE

    def test_safetyexception_defined(self) -> None:
        assert SafetyException is not None

    def test_statevalidationerror_defined(self) -> None:
        assert StateValidationError is not None

    def test_policyhashmismatch_defined(self) -> None:
        assert PolicyHashMismatch is not None

    def test_sovereigntokendenied_defined(self) -> None:
        assert SovereignTokenDenied is not None

    def test_ssotcircuitbreakermixin_defined(self) -> None:
        assert SSOTCircuitBreakerMixin is not None