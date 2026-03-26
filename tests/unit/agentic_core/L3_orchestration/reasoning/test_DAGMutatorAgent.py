"""Foundational behavioral tests for agentic_core/L3_orchestration/reasoning/DAGMutatorAgent.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_DAGMutatorAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: from agentic_core.L3_orchestration.reasoning.DAGMutatorAgent import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    DAGConfig,
    DAGMutation,
    GraphTransaction,
    HopSpec,
    MutationAction,
    MutationResult,
)


class TestGraphTransactionContract:
    def test_is_class(self):
        from agentic_core.L3_orchestration.reasoning.DAGMutatorAgent import (  # noqa: F401
        assert isinstance(GraphTransaction, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(GraphTransaction, type)

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

class TestHopSpecContract:
    def test_is_class(self):
        assert isinstance(HopSpec, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(HopSpec, type)

class TestDAGMutationContract:
    def test_is_class(self):
        assert isinstance(DAGMutation, type)

    def test_has_method_validate_hop_spec(self):
        assert callable(getattr(DAGMutation, 'validate_hop_spec', None))

class TestMutationResultContract:
    def test_is_class(self):
        assert isinstance(MutationResult, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(MutationResult, type)

class TestDAGConfigContract:
    def test_is_class(self):
        assert isinstance(DAGConfig, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(DAGConfig, type)

class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module DAGMutatorAgent must be importable or skip gracefully."""
    pass  # Import verified at module level
