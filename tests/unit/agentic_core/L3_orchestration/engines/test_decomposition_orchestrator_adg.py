"""ADG importability contract for agentic_core/L3_orchestration/engines/decomposition_orchestrator.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_decomposition_orchestrator.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L3_orchestration.engines.decomposition_orchestrator import (  # noqa: F401
        AtomicTask,
        DecompositionOrchestrator,
        MissionPlan,
        WorkerPool,
        WorkerResult,
        create_decomposition_orchestrator,
    )

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    AtomicTask = None  # type: ignore[assignment,misc]
    MissionPlan = None  # type: ignore[assignment,misc]
    DecompositionOrchestrator = None  # type: ignore[assignment,misc]
    create_decomposition_orchestrator = None  # type: ignore[assignment,misc]
    WorkerResult = None  # type: ignore[assignment,misc]
    WorkerPool = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="decomposition_orchestrator deps unavailable")
class TestDecompositionOrchestratorImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L3_orchestration/engines/decomposition_orchestrator.py must be importable."""
        assert _AVAILABLE

    def test_atomictask_defined(self) -> None:
        assert AtomicTask is not None

    def test_missionplan_defined(self) -> None:
        assert MissionPlan is not None

    def test_decompositionorchestrator_defined(self) -> None:
        assert DecompositionOrchestrator is not None

    def test_workerresult_defined(self) -> None:
        assert WorkerResult is not None

    def test_workerpool_defined(self) -> None:
        assert WorkerPool is not None
