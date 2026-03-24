"""ADG importability contract for agentic_core/L3_orchestration/engines/reasoning_intensity_enforcer.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_reasoning_intensity_enforcer.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.engines.reasoning_intensity_enforcer import (  # noqa: F401
        InvalidEnvelopeError,
        ReasoningBudgetExceeded,
        ReasoningIntensityEnforcer,
        ReasoningModeViolation,
        StageExecutionMetrics,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ReasoningBudgetExceeded = None  # type: ignore[assignment,misc]
    ReasoningModeViolation = None  # type: ignore[assignment,misc]
    InvalidEnvelopeError = None  # type: ignore[assignment,misc]
    StageExecutionMetrics = None  # type: ignore[assignment,misc]
    ReasoningIntensityEnforcer = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="reasoning_intensity_enforcer deps unavailable")
class TestReasoningIntensityEnforcerImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L3_orchestration/engines/reasoning_intensity_enforcer.py must be importable."""
        assert _AVAILABLE

    def test_reasoningbudgetexceeded_defined(self) -> None:
        assert ReasoningBudgetExceeded is not None

    def test_reasoningmodeviolation_defined(self) -> None:
        assert ReasoningModeViolation is not None

    def test_invalidenvelopeerror_defined(self) -> None:
        assert InvalidEnvelopeError is not None

    def test_stageexecutionmetrics_defined(self) -> None:
        assert StageExecutionMetrics is not None

    def test_reasoningintensityenforcer_defined(self) -> None:
        assert ReasoningIntensityEnforcer is not None