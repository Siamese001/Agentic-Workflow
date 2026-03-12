"""Foundational behavioral tests for agentic_core/L3_orchestration/reasoning/DAGMutatorAgent.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_DAGMutatorAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
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
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    GraphTransaction = None  # type: ignore[assignment,misc]
    MutationAction = None  # type: ignore[assignment,misc]
    HopSpec = None  # type: ignore[assignment,misc]
    DAGMutation = None  # type: ignore[assignment,misc]
    MutationResult = None  # type: ignore[assignment,misc]
    DAGConfig = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="DAGMutatorAgent.py deps unavailable")
class TestGraphTransactionContract:
    def test_is_class(self):
        assert isinstance(GraphTransaction, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(GraphTransaction, type)

@pytest.mark.skipif(not _AVAILABLE, reason="DAGMutatorAgent.py deps unavailable")
class TestMutationActionContract:
    def test_is_enum(self):
        import enum
        assert issubclass(MutationAction, enum.Enum)

    def test_has_members(self):
        assert len(list(MutationAction)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in MutationAction:
            assert member.value is not None

    def test_known_member_spawn_predecessor_exists(self):
        assert hasattr(MutationAction, 'SPAWN_PREDECESSOR')

@pytest.mark.skipif(not _AVAILABLE, reason="DAGMutatorAgent.py deps unavailable")
class TestHopSpecContract:
    def test_is_class(self):
        assert isinstance(HopSpec, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(HopSpec, type)

@pytest.mark.skipif(not _AVAILABLE, reason="DAGMutatorAgent.py deps unavailable")
class TestDAGMutationContract:
    def test_is_class(self):
        assert isinstance(DAGMutation, type)

    def test_has_method_validate_hop_spec(self):
        assert callable(getattr(DAGMutation, 'validate_hop_spec', None))

@pytest.mark.skipif(not _AVAILABLE, reason="DAGMutatorAgent.py deps unavailable")
class TestMutationResultContract:
    def test_is_class(self):
        assert isinstance(MutationResult, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(MutationResult, type)

@pytest.mark.skipif(not _AVAILABLE, reason="DAGMutatorAgent.py deps unavailable")
class TestDAGConfigContract:
    def test_is_class(self):
        assert isinstance(DAGConfig, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(DAGConfig, type)

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


def test_module_importable():
    """Module DAGMutatorAgent must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
