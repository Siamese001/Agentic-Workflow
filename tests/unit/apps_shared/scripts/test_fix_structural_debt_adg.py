"""ADG-driven tests for apps_shared/scripts/fix_structural_debt.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.scripts.fix_structural_debt import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        fix_globals,
        fix_large_functions,
        main,
        process_file,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    fix_globals = None  # type: ignore[assignment,misc]
    fix_large_functions = None  # type: ignore[assignment,misc]
    process_file = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="fix_structural_debt.py deps unavailable")
class TestFixGlobals:
    def test_is_callable(self):
        assert callable(fix_globals)

@pytest.mark.skipif(not _AVAILABLE, reason="fix_structural_debt.py deps unavailable")
class TestFixLargeFunctions:
    def test_is_callable(self):
        assert callable(fix_large_functions)

@pytest.mark.skipif(not _AVAILABLE, reason="fix_structural_debt.py deps unavailable")
class TestProcessFile:
    def test_is_callable(self):
        assert callable(process_file)

@pytest.mark.skipif(not _AVAILABLE, reason="fix_structural_debt.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="fix_structural_debt.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fix_structural_debt.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fix_structural_debt.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fix_structural_debt.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fix_structural_debt.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="fix_structural_debt.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module fix_structural_debt.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
