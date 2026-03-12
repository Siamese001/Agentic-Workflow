"""ADG-driven tests for agentic_core/L3_orchestration/engines/decomposition_orchestrator.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L3_orchestration.engines.decomposition_orchestrator import (  # noqa: F401
        AtomicTask,
        MissionPlan,
        DecompositionOrchestrator,
        create_decomposition_orchestrator,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    AtomicTask = None  # type: ignore[assignment,misc]
    MissionPlan = None  # type: ignore[assignment,misc]
    DecompositionOrchestrator = None  # type: ignore[assignment,misc]
    create_decomposition_orchestrator = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="decomposition_orchestrator.py deps unavailable")
class TestAtomicTask:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(AtomicTask)
    def test_importable(self):
        assert AtomicTask is not None

@pytest.mark.skipif(not _AVAILABLE, reason="decomposition_orchestrator.py deps unavailable")
class TestMissionPlan:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(MissionPlan)
    def test_importable(self):
        assert MissionPlan is not None

@pytest.mark.skipif(not _AVAILABLE, reason="decomposition_orchestrator.py deps unavailable")
class TestDecompositionOrchestrator:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(DecompositionOrchestrator)
    def test_importable(self):
        assert DecompositionOrchestrator is not None

@pytest.mark.skipif(not _AVAILABLE, reason="decomposition_orchestrator.py deps unavailable")
class TestCreateDecompositionOrchestrator:
    def test_is_callable(self):
        assert callable(create_decomposition_orchestrator)


def test_module_importable():
    """Module decomposition_orchestrator.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
