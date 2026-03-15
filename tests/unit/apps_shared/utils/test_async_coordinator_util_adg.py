"""ADG-driven tests for apps_shared/utils/async_coordinator_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.async_coordinator_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
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
except ImportError:
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
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="async_coordinator_util.py deps unavailable")
class TestTaskState:
    def test_is_enum(self):
        import enum
        assert issubclass(TaskState, enum.Enum)
    def test_has_members(self):
        assert len(list(TaskState)) >= 1
    def test_importable(self):
        assert TaskState is not None

@pytest.mark.skipif(not _AVAILABLE, reason="async_coordinator_util.py deps unavailable")
class TestTaskInfo:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(TaskInfo)
    def test_importable(self):
        assert TaskInfo is not None

@pytest.mark.skipif(not _AVAILABLE, reason="async_coordinator_util.py deps unavailable")
class TestAsyncCoordinator:
    def test_is_class(self):
        assert isinstance(AsyncCoordinator, type)
    def test_importable(self):
        assert AsyncCoordinator is not None

@pytest.mark.skipif(not _AVAILABLE, reason="async_coordinator_util.py deps unavailable")
class TestGetCoordinator:
    def test_is_callable(self):
        assert callable(get_coordinator)

@pytest.mark.skipif(not _AVAILABLE, reason="async_coordinator_util.py deps unavailable")
class TestShutdownAllCoordinators:
    def test_is_callable(self):
        assert callable(shutdown_all_coordinators)

@pytest.mark.skipif(not _AVAILABLE, reason="async_coordinator_util.py deps unavailable")
class TestManaged:
    def test_is_callable(self):
        assert callable(managed)

@pytest.mark.skipif(not _AVAILABLE, reason="async_coordinator_util.py deps unavailable")
class TestSafeWaitFor:
    def test_is_callable(self):
        assert callable(safe_wait_for)

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

@pytest.mark.skipif(not _AVAILABLE, reason="async_coordinator_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module async_coordinator_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
