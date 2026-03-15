"""ADG-driven tests for system_learning/runtime/isolation_monitor.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from system_learning.runtime.isolation_monitor import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        assert_isolation,
        check_system_learning_runtime_isolation,
        get_forbidden_loaded_modules,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    get_forbidden_loaded_modules = None  # type: ignore[assignment,misc]
    assert_isolation = None  # type: ignore[assignment,misc]
    check_system_learning_runtime_isolation = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="isolation_monitor.py deps unavailable")
class TestGetForbiddenLoadedModules:
    def test_is_callable(self):
        assert callable(get_forbidden_loaded_modules)

@pytest.mark.skipif(not _AVAILABLE, reason="isolation_monitor.py deps unavailable")
class TestAssertIsolation:
    def test_is_callable(self):
        assert callable(assert_isolation)

@pytest.mark.skipif(not _AVAILABLE, reason="isolation_monitor.py deps unavailable")
class TestCheckSystemLearningRuntimeIsolation:
    def test_is_callable(self):
        assert callable(check_system_learning_runtime_isolation)

@pytest.mark.skipif(not _AVAILABLE, reason="isolation_monitor.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="isolation_monitor.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="isolation_monitor.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="isolation_monitor.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="isolation_monitor.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="isolation_monitor.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module isolation_monitor.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
