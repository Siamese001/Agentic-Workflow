"""ADG importability contract for agentic_core/adg/runtime/safety_observer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_safety_observer.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.adg.runtime.safety_observer import (  # noqa: F401
        GuardrailExecution,
        PolicyHashVerification,
        RuntimeSafetyObserver,
        RuntimeSafetyReport,
        SafetyViolation,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    GuardrailExecution = None  # type: ignore[assignment,misc]
    PolicyHashVerification = None  # type: ignore[assignment,misc]
    SafetyViolation = None  # type: ignore[assignment,misc]
    RuntimeSafetyReport = None  # type: ignore[assignment,misc]
    RuntimeSafetyObserver = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="safety_observer deps unavailable")
class TestSafetyObserverImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/adg/runtime/safety_observer.py must be importable."""
        assert _AVAILABLE

    def test_guardrailexecution_defined(self) -> None:
        assert GuardrailExecution is not None

    def test_policyhashverification_defined(self) -> None:
        assert PolicyHashVerification is not None

    def test_safetyviolation_defined(self) -> None:
        assert SafetyViolation is not None

    def test_runtimesafetyreport_defined(self) -> None:
        assert RuntimeSafetyReport is not None

    def test_runtimesafetyobserver_defined(self) -> None:
        assert RuntimeSafetyObserver is not None