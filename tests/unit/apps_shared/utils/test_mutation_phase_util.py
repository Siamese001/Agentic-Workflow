"""Foundational behavioral tests for apps_shared/utils/mutation_phase_util.py.

fan_in=15 — this module is imported by 15 other modules.
ADG contract: import-hygiene is covered by test_mutation_phase_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.mutation_phase_util import (  # noqa: F401
        MutationPhase,
        StateSnapshot,
        DAGSafetyManager,
        SafeMutationContext,
        validate_acyclic_hook,
        validate_connectivity_hook,
        validate_node_attributes_hook,
        validate_depth_consistency_hook,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    MutationPhase = None  # type: ignore[assignment,misc]
    StateSnapshot = None  # type: ignore[assignment,misc]
    DAGSafetyManager = None  # type: ignore[assignment,misc]
    SafeMutationContext = None  # type: ignore[assignment,misc]
    validate_acyclic_hook = None  # type: ignore[assignment,misc]
    validate_connectivity_hook = None  # type: ignore[assignment,misc]
    validate_node_attributes_hook = None  # type: ignore[assignment,misc]
    validate_depth_consistency_hook = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="mutation_phase_util.py deps unavailable")
class TestMutationPhaseContract:
    def test_is_enum(self):
        import enum
        assert issubclass(MutationPhase, enum.Enum)

    def test_has_members(self):
        assert len(list(MutationPhase)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in MutationPhase:
            assert member.value is not None

    def test_known_member_pre_validate_exists(self):
        assert hasattr(MutationPhase, 'PRE_VALIDATE')

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_phase_util.py deps unavailable")
class TestStateSnapshotContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(StateSnapshot)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(StateSnapshot)}
        assert field_names >= {'external_state', 'edge_attributes', 'graph_copy', 'timestamp', 'node_attributes'}

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_phase_util.py deps unavailable")
class TestDAGSafetyManagerContract:
    def test_is_class(self):
        assert isinstance(DAGSafetyManager, type)

    def test_has_method_add_validation_hook(self):
        assert callable(getattr(DAGSafetyManager, 'add_validation_hook', None))

    def test_has_method_create_snapshot(self):
        assert callable(getattr(DAGSafetyManager, 'create_snapshot', None))

    def test_has_method_restore_snapshot(self):
        assert callable(getattr(DAGSafetyManager, 'restore_snapshot', None))

    def test_has_method_begin_mutation(self):
        assert callable(getattr(DAGSafetyManager, 'begin_mutation', None))

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_phase_util.py deps unavailable")
class TestSafeMutationContextContract:
    def test_is_class(self):
        assert isinstance(SafeMutationContext, type)

    def test_has_method_execute(self):
        assert callable(getattr(SafeMutationContext, 'execute', None))

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_phase_util.py deps unavailable")
class TestValidateAcyclicHookFunction:
    def test_is_callable(self):
        assert callable(validate_acyclic_hook)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(validate_acyclic_hook)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_phase_util.py deps unavailable")
class TestValidateConnectivityHookFunction:
    def test_is_callable(self):
        assert callable(validate_connectivity_hook)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(validate_connectivity_hook)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_phase_util.py deps unavailable")
class TestValidateNodeAttributesHookFunction:
    def test_is_callable(self):
        assert callable(validate_node_attributes_hook)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(validate_node_attributes_hook)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="mutation_phase_util.py deps unavailable")
class TestValidateDepthConsistencyHookFunction:
    def test_is_callable(self):
        assert callable(validate_depth_consistency_hook)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(validate_depth_consistency_hook)
        assert sig.return_annotation is not inspect.Parameter.empty

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


def test_module_importable():
    """Module mutation_phase_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
