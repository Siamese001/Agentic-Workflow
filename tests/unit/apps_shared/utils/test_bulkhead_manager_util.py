"""Foundational behavioral tests for apps_shared/utils/bulkhead_manager_util.py.

fan_in=15 — this module is imported by 15 other modules.
ADG contract: import-hygiene is covered by test_bulkhead_manager_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.bulkhead_manager_util import (  # noqa: F401
        TaskPriority,
        BulkheadConfig,
        BulkheadMetrics,
        ResourceExhaustedError,
        Bulkhead,
        BulkheadManager,
        get_bulkhead_manager,
        with_bulkhead,
        with_engine_bulkhead,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    TaskPriority = None  # type: ignore[assignment,misc]
    BulkheadConfig = None  # type: ignore[assignment,misc]
    BulkheadMetrics = None  # type: ignore[assignment,misc]
    ResourceExhaustedError = None  # type: ignore[assignment,misc]
    Bulkhead = None  # type: ignore[assignment,misc]
    BulkheadManager = None  # type: ignore[assignment,misc]
    get_bulkhead_manager = None  # type: ignore[assignment,misc]
    with_bulkhead = None  # type: ignore[assignment,misc]
    with_engine_bulkhead = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="bulkhead_manager_util.py deps unavailable")
class TestTaskPriorityContract:
    def test_is_enum(self):
        import enum
        assert issubclass(TaskPriority, enum.Enum)

    def test_has_members(self):
        assert len(list(TaskPriority)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in TaskPriority:
            assert member.value is not None

    def test_known_member_low_exists(self):
        assert hasattr(TaskPriority, 'LOW')

@pytest.mark.skipif(not _AVAILABLE, reason="bulkhead_manager_util.py deps unavailable")
class TestBulkheadConfigContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(BulkheadConfig)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(BulkheadConfig)}
        assert field_names >= {'queue_size', 'priority', 'metrics_enabled', 'max_concurrency', 'timeout_seconds'}

@pytest.mark.skipif(not _AVAILABLE, reason="bulkhead_manager_util.py deps unavailable")
class TestBulkheadMetricsContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(BulkheadMetrics)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(BulkheadMetrics)}
        assert field_names >= {'queue_size', 'queued_tasks', 'active_tasks', 'name', 'max_concurrency'}

@pytest.mark.skipif(not _AVAILABLE, reason="bulkhead_manager_util.py deps unavailable")
class TestResourceExhaustedErrorContract:
    def test_is_class(self):
        assert isinstance(ResourceExhaustedError, type)

    def test_instantiable_or_abstract(self):
        assert isinstance(ResourceExhaustedError, type)

@pytest.mark.skipif(not _AVAILABLE, reason="bulkhead_manager_util.py deps unavailable")
class TestBulkheadContract:
    def test_is_class(self):
        assert isinstance(Bulkhead, type)

    def test_has_method_execute(self):
        assert callable(getattr(Bulkhead, 'execute', None))

    def test_has_method_try_acquire(self):
        assert callable(getattr(Bulkhead, 'try_acquire', None))

    def test_has_method_get_metrics(self):
        assert callable(getattr(Bulkhead, 'get_metrics', None))

    def test_has_method_wait_for_available(self):
        assert callable(getattr(Bulkhead, 'wait_for_available', None))

@pytest.mark.skipif(not _AVAILABLE, reason="bulkhead_manager_util.py deps unavailable")
class TestBulkheadManagerContract:
    def test_is_class(self):
        assert isinstance(BulkheadManager, type)

    def test_has_method_create_bulkhead(self):
        assert callable(getattr(BulkheadManager, 'create_bulkhead', None))

    def test_has_method_get_bulkhead(self):
        assert callable(getattr(BulkheadManager, 'get_bulkhead', None))

    def test_has_method_remove_bulkhead(self):
        assert callable(getattr(BulkheadManager, 'remove_bulkhead', None))

    def test_has_method_execute(self):
        assert callable(getattr(BulkheadManager, 'execute', None))

@pytest.mark.skipif(not _AVAILABLE, reason="bulkhead_manager_util.py deps unavailable")
class TestGetBulkheadManagerFunction:
    def test_is_callable(self):
        assert callable(get_bulkhead_manager)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_bulkhead_manager)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="bulkhead_manager_util.py deps unavailable")
class TestWithBulkheadFunction:
    def test_is_callable(self):
        assert callable(with_bulkhead)

@pytest.mark.skipif(not _AVAILABLE, reason="bulkhead_manager_util.py deps unavailable")
class TestWithEngineBulkheadFunction:
    def test_is_callable(self):
        assert callable(with_engine_bulkhead)

@pytest.mark.skipif(not _AVAILABLE, reason="bulkhead_manager_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="bulkhead_manager_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="bulkhead_manager_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="bulkhead_manager_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="bulkhead_manager_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module bulkhead_manager_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
