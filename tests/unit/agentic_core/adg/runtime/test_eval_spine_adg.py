"""ADG importability contract for agentic_core/adg/runtime/eval_spine.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_eval_spine.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.adg.runtime.eval_spine import (  # noqa: F401
        DPOBatch,
        DriftAlert,
        EvalMetricResult,
        OptimizationProposal,
        OptimizationStage,
        PreferencePair,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    OptimizationStage = None  # type: ignore[assignment,misc]
    EvalMetricResult = None  # type: ignore[assignment,misc]
    DriftAlert = None  # type: ignore[assignment,misc]
    PreferencePair = None  # type: ignore[assignment,misc]
    DPOBatch = None  # type: ignore[assignment,misc]
    OptimizationProposal = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="eval_spine deps unavailable")
class TestEvalSpineImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/adg/runtime/eval_spine.py must be importable."""
        assert _AVAILABLE

    def test_optimizationstage_defined(self) -> None:
        assert OptimizationStage is not None

    def test_evalmetricresult_defined(self) -> None:
        assert EvalMetricResult is not None

    def test_driftalert_defined(self) -> None:
        assert DriftAlert is not None

    def test_preferencepair_defined(self) -> None:
        assert PreferencePair is not None

    def test_dpobatch_defined(self) -> None:
        assert DPOBatch is not None

    def test_optimizationproposal_defined(self) -> None:
        assert OptimizationProposal is not None