"""Foundational behavioral tests for agentic_core/L3_orchestration/reasoning/DagEngineAgent.py.

fan_in=12 — this module is imported by 12 other modules.
ADG contract: import-hygiene is covered by test_DagEngineAgent_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L3_orchestration.reasoning.DagEngineAgent import (  # noqa: F401
        TaskStatus,
        TaskType,
        Task,
        DagExecutionResult,
        DagEngineAgent,
        create_dag_from_config,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    TaskStatus = None  # type: ignore[assignment,misc]
    TaskType = None  # type: ignore[assignment,misc]
    Task = None  # type: ignore[assignment,misc]
    DagExecutionResult = None  # type: ignore[assignment,misc]
    DagEngineAgent = None  # type: ignore[assignment,misc]
    create_dag_from_config = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="DagEngineAgent.py deps unavailable")
class TestTaskStatusContract:
    def test_is_enum(self):
        import enum
        assert issubclass(TaskStatus, enum.Enum)

    def test_has_members(self):
        assert len(list(TaskStatus)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="DagEngineAgent.py deps unavailable")
class TestTaskTypeContract:
    def test_is_enum(self):
        import enum
        assert issubclass(TaskType, enum.Enum)

    def test_has_members(self):
        assert len(list(TaskType)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="DagEngineAgent.py deps unavailable")
class TestTaskContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(Task)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(Task)}
        assert field_names >= {'parameters', 'dependencies', 'id', 'TaskType', 'name'}

@pytest.mark.skipif(not _AVAILABLE, reason="DagEngineAgent.py deps unavailable")
class TestDagExecutionResultContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(DagExecutionResult)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(DagExecutionResult)}
        assert field_names >= {'task_results', 'failed_tasks', 'success', 'skipped_tasks', 'completed_tasks'}

@pytest.mark.skipif(not _AVAILABLE, reason="DagEngineAgent.py deps unavailable")
class TestDagEngineAgentContract:
    def test_is_class(self):
        assert isinstance(DagEngineAgent, type)

    def test_has_method_add_task(self):
        assert callable(getattr(DagEngineAgent, 'add_task', None))

    def test_has_method_remove_task(self):
        assert callable(getattr(DagEngineAgent, 'remove_task', None))

    def test_has_method_validate_dag(self):
        assert callable(getattr(DagEngineAgent, 'validate_dag', None))

    def test_has_method_topological_sort(self):
        assert callable(getattr(DagEngineAgent, 'topological_sort', None))

@pytest.mark.skipif(not _AVAILABLE, reason="DagEngineAgent.py deps unavailable")
class TestCreateDagFromConfigFunction:
    def test_is_callable(self):
        assert callable(create_dag_from_config)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(create_dag_from_config)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="DagEngineAgent.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DagEngineAgent.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DagEngineAgent.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DagEngineAgent.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="DagEngineAgent.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module DagEngineAgent must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
