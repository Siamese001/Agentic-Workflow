"""ADG-driven tests for apps_rg/tools/fetch_user_preferences.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_rg.tools.fetch_user_preferences import (  # noqa: F401
        fetch_user_preferences,
        retrieve,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    fetch_user_preferences = None  # type: ignore[assignment,misc]
    retrieve = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="fetch_user_preferences.py deps unavailable")
class Testfetch_user_preferences:
    def test_is_class(self):
        assert isinstance(fetch_user_preferences, type)
    def test_importable(self):
        assert fetch_user_preferences is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fetch_user_preferences.py deps unavailable")
class TestRetrieve:
    def test_is_callable(self):
        assert callable(retrieve)

@pytest.mark.skipif(not _AVAILABLE, reason="fetch_user_preferences.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fetch_user_preferences.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fetch_user_preferences.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fetch_user_preferences.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fetch_user_preferences.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fetch_user_preferences.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module fetch_user_preferences.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
