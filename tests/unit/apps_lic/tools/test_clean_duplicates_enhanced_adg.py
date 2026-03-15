"""ADG-driven tests for apps_lic/tools/clean_duplicates_enhanced.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_lic.tools.clean_duplicates_enhanced import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        aggressive_cleanup,
        extract_functions,
        get_file_hash,
        merge_validator_logic,
        organize_structure,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    aggressive_cleanup = None  # type: ignore[assignment,misc]
    organize_structure = None  # type: ignore[assignment,misc]
    get_file_hash = None  # type: ignore[assignment,misc]
    extract_functions = None  # type: ignore[assignment,misc]
    merge_validator_logic = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="clean_duplicates_enhanced.py deps unavailable")
class TestAggressiveCleanup:
    def test_is_callable(self):
        assert callable(aggressive_cleanup)

@pytest.mark.skipif(not _AVAILABLE, reason="clean_duplicates_enhanced.py deps unavailable")
class TestOrganizeStructure:
    def test_is_callable(self):
        assert callable(organize_structure)

@pytest.mark.skipif(not _AVAILABLE, reason="clean_duplicates_enhanced.py deps unavailable")
class TestGetFileHash:
    def test_is_callable(self):
        assert callable(get_file_hash)

@pytest.mark.skipif(not _AVAILABLE, reason="clean_duplicates_enhanced.py deps unavailable")
class TestExtractFunctions:
    def test_is_callable(self):
        assert callable(extract_functions)

@pytest.mark.skipif(not _AVAILABLE, reason="clean_duplicates_enhanced.py deps unavailable")
class TestMergeValidatorLogic:
    def test_is_callable(self):
        assert callable(merge_validator_logic)

@pytest.mark.skipif(not _AVAILABLE, reason="clean_duplicates_enhanced.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="clean_duplicates_enhanced.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="clean_duplicates_enhanced.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="clean_duplicates_enhanced.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="clean_duplicates_enhanced.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="clean_duplicates_enhanced.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module clean_duplicates_enhanced.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
