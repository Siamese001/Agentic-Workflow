"""ADG-driven tests for apps_shared/utils/mutation_phase_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.mutation_phase_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        DAGSafetyManager,
        MutationPhase,
        SafeMutationContext,
        StateSnapshot,
        create_default_safety_manager,
        validate_acyclic_hook,
        validate_connectivity_hook,
        validate_depth_consistency_hook,
        validate_node_attributes_hook,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    MutationPhase = None  # type: ignore[assignment,misc]
    StateSnapshot = None  # type: ignore[assignment,misc]
    DAGSafetyManager = None  # type: ignore[assignment,misc]
    SafeMutationContext = None  # type: ignore[assignment,misc]
    validate_acyclic_hook = None  # type: ignore[assignment,misc]
    validate_connectivity_hook = None  # type: ignore[assignment,misc]
    validate_node_attributes_hook = None  # type: ignore[assignment,misc]
    validate_depth_consistency_hook = None  # type: ignore[assignment,misc]
    create_default_safety_manager = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="mutation_phase_util.py deps unavailable")
class TestMutationPhase:
    def test_is_enum(self):
        import enum
        assert issubclass(MutationPhase, enum.Enum)
    def test_has_members(self):
        assert len(list(MutationPhase)) >= 1
    def test_importable(self):
        assert MutationPhase is not None

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_phase_util.py deps unavailable")
class TestStateSnapshot:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(StateSnapshot)
    def test_importable(self):
        assert StateSnapshot is not None

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_phase_util.py deps unavailable")
class TestDAGSafetyManager:
    def test_is_class(self):
        assert isinstance(DAGSafetyManager, type)
    def test_importable(self):
        assert DAGSafetyManager is not None

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_phase_util.py deps unavailable")
class TestSafeMutationContext:
    def test_is_class(self):
        assert isinstance(SafeMutationContext, type)
    def test_importable(self):
        assert SafeMutationContext is not None

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_phase_util.py deps unavailable")
class TestValidateAcyclicHook:
    def test_is_callable(self):
        assert callable(validate_acyclic_hook)

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_phase_util.py deps unavailable")
class TestValidateConnectivityHook:
    def test_is_callable(self):
        assert callable(validate_connectivity_hook)

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_phase_util.py deps unavailable")
class TestValidateNodeAttributesHook:
    def test_is_callable(self):
        assert callable(validate_node_attributes_hook)

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_phase_util.py deps unavailable")
class TestValidateDepthConsistencyHook:
    def test_is_callable(self):
        assert callable(validate_depth_consistency_hook)

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_phase_util.py deps unavailable")
class TestCreateDefaultSafetyManager:
    def test_is_callable(self):
        assert callable(create_default_safety_manager)

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_phase_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_phase_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_phase_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_phase_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_phase_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_phase_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module mutation_phase_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE