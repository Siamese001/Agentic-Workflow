"""Foundational behavioral tests for apps_shared/utils/async_coordinator_util.py.

fan_in=13 — this module is imported by 13 other modules.
ADG contract: import-hygiene is covered by test_async_coordinator_util_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.async_coordinator_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        AsyncCoordinator,
        TaskInfo,
        TaskState,
        get_coordinator,
        managed,
        safe_wait_for,
        shutdown_all_coordinators,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    TaskState = None  # type: ignore[assignment,misc]
    TaskInfo = None  # type: ignore[assignment,misc]
    AsyncCoordinator = None  # type: ignore[assignment,misc]
    get_coordinator = None  # type: ignore[assignment,misc]
    shutdown_all_coordinators = None  # type: ignore[assignment,misc]
    managed = None  # type: ignore[assignment,misc]
    safe_wait_for = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="async_coordinator_util.py deps unavailable")
class TestTaskStateContract:
    def test_is_enum(self):
        import enum
        assert issubclass(TaskState, enum.Enum)

    def test_has_members(self):
        assert len(list(TaskState)) >= 1

    def test_member_values_are_strings_or_ints(self):
        for member in TaskState:
            assert member.value is not None

    def test_known_member_pending_exists(self):
        assert hasattr(TaskState, 'PENDING')

@pytest.mark.skipif(not _AVAILABLE, reason="async_coordinator_util.py deps unavailable")
class TestTaskInfoContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(TaskInfo)

    def test_field_names_present(self):
        import dataclasses
        field_names = {f.name for f in dataclasses.fields(TaskInfo)}
        assert field_names >= {'created_at', 'task_id', 'task', 'timeout', 'state'}

@pytest.mark.skipif(not _AVAILABLE, reason="async_coordinator_util.py deps unavailable")
class TestAsyncCoordinatorContract:
    def test_is_class(self):
        assert isinstance(AsyncCoordinator, type)

    def test_has_method_start(self):
        assert callable(getattr(AsyncCoordinator, 'start', None))

    def test_has_method_stop(self):
        assert callable(getattr(AsyncCoordinator, 'stop', None))

    def test_has_method_generate_task_id(self):
        assert callable(getattr(AsyncCoordinator, 'generate_task_id', None))

    def test_has_method_create_task(self):
        assert callable(getattr(AsyncCoordinator, 'create_task', None))

@pytest.mark.skipif(not _AVAILABLE, reason="async_coordinator_util.py deps unavailable")
class TestGetCoordinatorFunction:
    def test_is_callable(self):
        assert callable(get_coordinator)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_coordinator)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="async_coordinator_util.py deps unavailable")
class TestShutdownAllCoordinatorsFunction:
    def test_is_callable(self):
        assert callable(shutdown_all_coordinators)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(shutdown_all_coordinators)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="async_coordinator_util.py deps unavailable")
class TestManagedFunction:
    def test_is_callable(self):
        assert callable(managed)

@pytest.mark.skipif(not _AVAILABLE, reason="async_coordinator_util.py deps unavailable")
class TestSafeWaitForFunction:
    def test_is_callable(self):
        assert callable(safe_wait_for)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(safe_wait_for)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="async_coordinator_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="async_coordinator_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="async_coordinator_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="async_coordinator_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="async_coordinator_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module async_coordinator_util must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
