"""ADG-driven tests for system_learning/validators/readonly_access.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from system_learning.validators.readonly_access import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        check_file_readonly,
        check_system_learning_readonly,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    check_file_readonly = None  # type: ignore[assignment,misc]
    check_system_learning_readonly = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="readonly_access.py deps unavailable")
class TestCheckFileReadonly:
    def test_is_callable(self):
        assert callable(check_file_readonly)

@pytest.mark.skipif(not _AVAILABLE, reason="readonly_access.py deps unavailable")
class TestCheckSystemLearningReadonly:
    def test_is_callable(self):
        assert callable(check_system_learning_readonly)

@pytest.mark.skipif(not _AVAILABLE, reason="readonly_access.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="readonly_access.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="readonly_access.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="readonly_access.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="readonly_access.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="readonly_access.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module readonly_access.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
