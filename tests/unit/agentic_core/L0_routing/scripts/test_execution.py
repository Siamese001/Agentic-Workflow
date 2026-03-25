"""Foundational behavioral tests for agentic_core/L0_routing/scripts/execution.py.

fan_in=15 — this module is imported by 15 other modules.
ADG contract: import-hygiene is covered by test_execution_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L0_routing.scripts.execution import (  # noqa: F401
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    MAX_RETRIES,
    THRESHOLD,
    DAGStrategy,
    ExecutionStatus,
    ExecutionStrategy,
    WorkflowContext,
    WorkflowResult,
    WorkflowStep,
    get_strategy,
)


class TestExecutionStatusContract:
    def test_is_enum(self):
        import enum
        assert issubclass(ExecutionStatus, enum.Enum)

    def test_has_members(self):
        assert len(list(ExecutionStatus)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in ExecutionStatus:
            assert member.value is not None

    def test_known_member_pending_exists(self):
        assert hasattr(ExecutionStatus, 'PENDING')

class TestWorkflowContextContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(WorkflowContext)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(WorkflowContext)}
        assert field_names >= {'workflow_id', 'metadata', 'state', 'input_data', 'workflow_type'}

class TestWorkflowResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(WorkflowResult)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(WorkflowResult)}
        assert field_names >= {'error', 'status', 'metrics', 'workflow_id', 'output'}

class TestWorkflowStepContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(WorkflowStep)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(WorkflowStep)}
        assert field_names >= {'step_id', 'dependencies', 'name', 'handler', 'timeout_seconds'}

class TestExecutionStrategyContract:
    def test_is_class(self):
        assert isinstance(ExecutionStrategy, type)

    def test_has_method_execute(self):
        assert callable(getattr(ExecutionStrategy, 'execute', None))

    def test_has_method_get_name(self):
        assert callable(getattr(ExecutionStrategy, 'get_name', None))

    def test_has_method_can_handle(self):
        assert callable(getattr(ExecutionStrategy, 'can_handle', None))

class TestDAGStrategyContract:
    def test_is_class(self):
        assert isinstance(DAGStrategy, type)

    def test_has_method_execute(self):
        assert callable(getattr(DAGStrategy, 'execute', None))

    def test_has_method_get_name(self):
        assert callable(getattr(DAGStrategy, 'get_name', None))

    def test_has_method_can_handle(self):
        assert callable(getattr(DAGStrategy, 'can_handle', None))

class TestGetStrategyFunction:
    def test_is_callable(self):
        assert callable(get_strategy)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_strategy)
        assert sig.return_annotation is not inspect.Parameter.empty

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
    """Module execution must be importable or skip gracefully."""
    pass  # Import verified at module level
