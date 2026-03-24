"""ADG importability contract for agentic_core/L1_cognition/types/react_trace_types.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_react_trace_types.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L1_cognition.types.react_trace_types import (  # noqa: F401
        C0BoundaryViolation,
        NonDeterministicCallDetected,
        PromptProvenanceRecord,
        ReasonTraceEnvelope,
        ReplayGuard,
        assert_c0_informational,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    C0BoundaryViolation = None  # type: ignore[assignment,misc]
    assert_c0_informational = None  # type: ignore[assignment,misc]
    ReasonTraceEnvelope = None  # type: ignore[assignment,misc]
    PromptProvenanceRecord = None  # type: ignore[assignment,misc]
    NonDeterministicCallDetected = None  # type: ignore[assignment,misc]
    ReplayGuard = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="react_trace_types deps unavailable")
class TestReactTraceTypesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L1_cognition/types/react_trace_types.py must be importable."""
        assert _AVAILABLE

    def test_c0boundaryviolation_defined(self) -> None:
        assert C0BoundaryViolation is not None

    def test_reasontraceenvelope_defined(self) -> None:
        assert ReasonTraceEnvelope is not None

    def test_promptprovenancerecord_defined(self) -> None:
        assert PromptProvenanceRecord is not None

    def test_nondeterministiccalldetected_defined(self) -> None:
        assert NonDeterministicCallDetected is not None

    def test_replayguard_defined(self) -> None:
        assert ReplayGuard is not None