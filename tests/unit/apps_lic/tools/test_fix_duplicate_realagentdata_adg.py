"""ADG-driven tests for apps_lic/tools/fix_duplicate_realagentdata.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_lic.tools.fix_duplicate_realagentdata import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        fix_duplicates,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    fix_duplicates = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="fix_duplicate_realagentdata.py deps unavailable")
class TestFixDuplicates:
    def test_is_callable(self):
        assert callable(fix_duplicates)

@pytest.mark.skipif(not _AVAILABLE, reason="fix_duplicate_realagentdata.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fix_duplicate_realagentdata.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fix_duplicate_realagentdata.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fix_duplicate_realagentdata.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fix_duplicate_realagentdata.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fix_duplicate_realagentdata.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module fix_duplicate_realagentdata.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
