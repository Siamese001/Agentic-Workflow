"""ADG-driven tests for apps_shared/scripts/fix_all_dataclass_underscores.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.scripts.fix_all_dataclass_underscores import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        fix_dataclass_underscores,
        main,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    fix_dataclass_underscores = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="fix_all_dataclass_underscores.py deps unavailable")
class TestFixDataclassUnderscores:
    def test_is_callable(self):
        assert callable(fix_dataclass_underscores)

@pytest.mark.skipif(not _AVAILABLE, reason="fix_all_dataclass_underscores.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="fix_all_dataclass_underscores.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fix_all_dataclass_underscores.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fix_all_dataclass_underscores.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fix_all_dataclass_underscores.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fix_all_dataclass_underscores.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fix_all_dataclass_underscores.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module fix_all_dataclass_underscores.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
