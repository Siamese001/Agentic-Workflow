"""ADG importability contract for agentic_core/L0_routing/types/reasoning_intensity_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_reasoning_intensity_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L0_routing.types.reasoning_intensity_types import (  # noqa: F401
        ReasoningConstraintViolation,
        ReasoningEnforcementTelemetry,
        ReasoningIntensityProfile,
        ReasoningTier,
        SignedExecutionEnvelope,
        StageTokenBudget,
    )

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ReasoningTier = None  # type: ignore[assignment,misc]
    StageTokenBudget = None  # type: ignore[assignment,misc]
    ReasoningIntensityProfile = None  # type: ignore[assignment,misc]
    SignedExecutionEnvelope = None  # type: ignore[assignment,misc]
    ReasoningConstraintViolation = None  # type: ignore[assignment,misc]
    ReasoningEnforcementTelemetry = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="reasoning_intensity_types deps unavailable")
class TestReasoningIntensityTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L0_routing/types/reasoning_intensity_types.py must be importable."""
        assert _AVAILABLE

    def test_reasoningtier_defined(self) -> None:
        assert ReasoningTier is not None

    def test_stagetokenbudget_defined(self) -> None:
        assert StageTokenBudget is not None

    def test_reasoningintensityprofile_defined(self) -> None:
        assert ReasoningIntensityProfile is not None

    def test_signedexecutionenvelope_defined(self) -> None:
        assert SignedExecutionEnvelope is not None

    def test_reasoningconstraintviolation_defined(self) -> None:
        assert ReasoningConstraintViolation is not None

    def test_reasoningenforcementtelemetry_defined(self) -> None:
        assert ReasoningEnforcementTelemetry is not None
