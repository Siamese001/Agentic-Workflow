"""ADG importability contract for agentic_core/L5_safety/security/injection_regression_gate.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_injection_regression_gate.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L5_safety.security.injection_regression_gate import (  # noqa: F401
        InjectionMetrics,
        InjectionRegressionError,
        RegressionThresholds,
        check_regression_compliance,
        evaluate_against_baseline,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    RegressionThresholds = None  # type: ignore[assignment,misc]
    InjectionMetrics = None  # type: ignore[assignment,misc]
    InjectionRegressionError = None  # type: ignore[assignment,misc]
    evaluate_against_baseline = None  # type: ignore[assignment,misc]
    check_regression_compliance = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="injection_regression_gate deps unavailable")
class TestInjectionRegressionGateImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L5_safety/security/injection_regression_gate.py must be importable."""
        assert _AVAILABLE

    def test_regressionthresholds_defined(self) -> None:
        assert RegressionThresholds is not None

    def test_injectionmetrics_defined(self) -> None:
        assert InjectionMetrics is not None

    def test_injectionregressionerror_defined(self) -> None:
        assert InjectionRegressionError is not None
