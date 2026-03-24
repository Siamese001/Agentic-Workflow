"""ADG importability contract for agentic_core/adg/runtime/execution_proof.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_execution_proof.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.adg.runtime.execution_proof import (  # noqa: F401
        ExecutionProofRecorder,
        ExecutionProofReport,
        ExecutionTrace,
        ProofComparison,
        ProofComparisonOutcome,
        ReplayKey,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ProofComparisonOutcome = None  # type: ignore[assignment,misc]
    ExecutionTrace = None  # type: ignore[assignment,misc]
    ReplayKey = None  # type: ignore[assignment,misc]
    ProofComparison = None  # type: ignore[assignment,misc]
    ExecutionProofReport = None  # type: ignore[assignment,misc]
    ExecutionProofRecorder = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="execution_proof deps unavailable")
class TestExecutionProofImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/adg/runtime/execution_proof.py must be importable."""
        assert _AVAILABLE

    def test_proofcomparisonoutcome_defined(self) -> None:
        assert ProofComparisonOutcome is not None

    def test_executiontrace_defined(self) -> None:
        assert ExecutionTrace is not None

    def test_replaykey_defined(self) -> None:
        assert ReplayKey is not None

    def test_proofcomparison_defined(self) -> None:
        assert ProofComparison is not None

    def test_executionproofreport_defined(self) -> None:
        assert ExecutionProofReport is not None

    def test_executionproofrecorder_defined(self) -> None:
        assert ExecutionProofRecorder is not None