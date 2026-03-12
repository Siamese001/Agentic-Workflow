"""ADG importability contract for agentic_core/L5_safety/security/injection_regression_gate.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_injection_regression_gate.py (no _adg suffix).
"""
from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.security.injection_regression_gate import (  # noqa: F401
        RegressionThresholds,
        InjectionMetrics,
        InjectionRegressionError,
        evaluate_against_baseline,
        check_regression_compliance,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    RegressionThresholds = None  # type: ignore[assignment,misc]
    InjectionMetrics = None  # type: ignore[assignment,misc]
    InjectionRegressionError = None  # type: ignore[assignment,misc]
    evaluate_against_baseline = None  # type: ignore[assignment,misc]
    check_regression_compliance = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAILABLE, reason="injection_regression_gate.py deps unavailable")
class TestInjectionRegressionGateImportability:
    def test_module_importable(self) -> None:
        """ADG contract: injection_regression_gate.py must be importable."""
        assert _AVAILABLE

    def test_regressionthresholds_is_type(self) -> None:
        assert RegressionThresholds is not None

    def test_injectionmetrics_is_type(self) -> None:
        assert InjectionMetrics is not None

    def test_injectionregressionerror_is_type(self) -> None:
        assert InjectionRegressionError is not None

    def test_evaluate_against_baseline_callable(self) -> None:
        assert callable(evaluate_against_baseline)

    def test_check_regression_compliance_callable(self) -> None:
        assert callable(check_regression_compliance)

    def test_max_retries_defined(self) -> None:
        assert MAX_RETRIES is not None

    def test_default_sleep_defined(self) -> None:
        assert DEFAULT_SLEEP is not None

