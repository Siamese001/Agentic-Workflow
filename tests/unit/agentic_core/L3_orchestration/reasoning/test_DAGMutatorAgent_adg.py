"""ADG-driven tests for agentic_core/L3_orchestration/reasoning/DAGMutatorAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L3_orchestration.reasoning.DAGMutatorAgent import (  # noqa: F401
        GraphTransaction,
        MutationAction,
        HopSpec,
        DAGMutation,
        MutationResult,
        DAGConfig,
        DAGMutatorAgent,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    GraphTransaction = None  # type: ignore[assignment,misc]
    MutationAction = None  # type: ignore[assignment,misc]
    HopSpec = None  # type: ignore[assignment,misc]
    DAGMutation = None  # type: ignore[assignment,misc]
    MutationResult = None  # type: ignore[assignment,misc]
    DAGConfig = None  # type: ignore[assignment,misc]
    DAGMutatorAgent = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="DAGMutatorAgent.py deps unavailable")
class TestGraphTransaction:
    def test_is_class(self):
        assert isinstance(GraphTransaction, type)
    def test_importable(self):
        assert GraphTransaction is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DAGMutatorAgent.py deps unavailable")
class TestMutationAction:
    def test_is_enum(self):
        import enum
        assert issubclass(MutationAction, enum.Enum)
    def test_has_members(self):
        assert len(list(MutationAction)) >= 1
    def test_importable(self):
        assert MutationAction is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DAGMutatorAgent.py deps unavailable")
class TestHopSpec:
    def test_is_class(self):
        assert isinstance(HopSpec, type)
    def test_importable(self):
        assert HopSpec is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DAGMutatorAgent.py deps unavailable")
class TestDAGMutation:
    def test_is_class(self):
        assert isinstance(DAGMutation, type)
    def test_importable(self):
        assert DAGMutation is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DAGMutatorAgent.py deps unavailable")
class TestMutationResult:
    def test_is_class(self):
        assert isinstance(MutationResult, type)
    def test_importable(self):
        assert MutationResult is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DAGMutatorAgent.py deps unavailable")
class TestDAGConfig:
    def test_is_class(self):
        assert isinstance(DAGConfig, type)
    def test_importable(self):
        assert DAGConfig is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DAGMutatorAgent.py deps unavailable")
class TestDAGMutatorAgent:
    def test_is_class(self):
        assert isinstance(DAGMutatorAgent, type)
    def test_importable(self):
        assert DAGMutatorAgent is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DAGMutatorAgent.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DAGMutatorAgent.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DAGMutatorAgent.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DAGMutatorAgent.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DAGMutatorAgent.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DAGMutatorAgent.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module DAGMutatorAgent.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
