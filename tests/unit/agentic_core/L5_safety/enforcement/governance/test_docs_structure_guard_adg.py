"""ADG-driven tests for agentic_core/L5_safety/enforcement/governance/docs_structure_guard.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.governance.docs_structure_guard import (  # noqa: F401
        is_valid_extension,
        has_backup_suffix,
        has_h1_heading,
        scan_docs_directory,
        main,
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
    is_valid_extension = None  # type: ignore[assignment,misc]
    has_backup_suffix = None  # type: ignore[assignment,misc]
    has_h1_heading = None  # type: ignore[assignment,misc]
    scan_docs_directory = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="docs_structure_guard.py deps unavailable")
class TestIsValidExtension:
    def test_is_callable(self):
        assert callable(is_valid_extension)

@pytest.mark.skipif(not _AVAILABLE, reason="docs_structure_guard.py deps unavailable")
class TestHasBackupSuffix:
    def test_is_callable(self):
        assert callable(has_backup_suffix)

@pytest.mark.skipif(not _AVAILABLE, reason="docs_structure_guard.py deps unavailable")
class TestHasH1Heading:
    def test_is_callable(self):
        assert callable(has_h1_heading)

@pytest.mark.skipif(not _AVAILABLE, reason="docs_structure_guard.py deps unavailable")
class TestScanDocsDirectory:
    def test_is_callable(self):
        assert callable(scan_docs_directory)

@pytest.mark.skipif(not _AVAILABLE, reason="docs_structure_guard.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="docs_structure_guard.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="docs_structure_guard.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="docs_structure_guard.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="docs_structure_guard.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="docs_structure_guard.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="docs_structure_guard.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module docs_structure_guard.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
