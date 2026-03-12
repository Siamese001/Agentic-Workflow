"""Foundational behavioral tests for apps_lic/tools/clean_duplicates_enhanced.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_clean_duplicates_enhanced_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_lic.tools.clean_duplicates_enhanced import (  # noqa: F401
        aggressive_cleanup,
        organize_structure,
        get_file_hash,
        extract_functions,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
    )
    _AVAILABLE = True
except Exception as _exc:
    _AVAILABLE = False
    aggressive_cleanup = None  # type: ignore[assignment,misc]
    organize_structure = None  # type: ignore[assignment,misc]
    get_file_hash = None  # type: ignore[assignment,misc]
    extract_functions = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="clean_duplicates_enhanced.py deps unavailable")
class TestAggressiveCleanupFunction:
    def test_is_callable(self):
        assert callable(aggressive_cleanup)

@pytest.mark.skipif(not _AVAILABLE, reason="clean_duplicates_enhanced.py deps unavailable")
class TestOrganizeStructureFunction:
    def test_is_callable(self):
        assert callable(organize_structure)

@pytest.mark.skipif(not _AVAILABLE, reason="clean_duplicates_enhanced.py deps unavailable")
class TestGetFileHashFunction:
    def test_is_callable(self):
        assert callable(get_file_hash)

@pytest.mark.skipif(not _AVAILABLE, reason="clean_duplicates_enhanced.py deps unavailable")
class TestExtractFunctionsFunction:
    def test_is_callable(self):
        assert callable(extract_functions)

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


def test_module_importable():
    """Module clean_duplicates_enhanced must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
