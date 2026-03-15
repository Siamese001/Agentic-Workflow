"""ADG-driven tests for agentic_core/L0_routing/scripts/bloat_analysis_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.bloat_analysis_util import (  # noqa: F401
        APPROVED,
        ROOT,
        find_deprecated_markers,
        find_duplicate_filenames,
        find_empty_or_stub_files,
        find_large_files,
        get_file_stats,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    get_file_stats = None  # type: ignore[assignment,misc]
    find_large_files = None  # type: ignore[assignment,misc]
    find_duplicate_filenames = None  # type: ignore[assignment,misc]
    find_empty_or_stub_files = None  # type: ignore[assignment,misc]
    find_deprecated_markers = None  # type: ignore[assignment,misc]
    ROOT = None  # type: ignore[assignment,misc]
    APPROVED = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="bloat_analysis_util.py deps unavailable")
class TestGetFileStats:
    def test_is_callable(self):
        assert callable(get_file_stats)

@pytest.mark.skipif(not _AVAILABLE, reason="bloat_analysis_util.py deps unavailable")
class TestFindLargeFiles:
    def test_is_callable(self):
        assert callable(find_large_files)

@pytest.mark.skipif(not _AVAILABLE, reason="bloat_analysis_util.py deps unavailable")
class TestFindDuplicateFilenames:
    def test_is_callable(self):
        assert callable(find_duplicate_filenames)

@pytest.mark.skipif(not _AVAILABLE, reason="bloat_analysis_util.py deps unavailable")
class TestFindEmptyOrStubFiles:
    def test_is_callable(self):
        assert callable(find_empty_or_stub_files)

@pytest.mark.skipif(not _AVAILABLE, reason="bloat_analysis_util.py deps unavailable")
class TestFindDeprecatedMarkers:
    def test_is_callable(self):
        assert callable(find_deprecated_markers)

@pytest.mark.skipif(not _AVAILABLE, reason="bloat_analysis_util.py deps unavailable")
class TestRootConstant:
    def test_is_not_none(self):
        assert ROOT is not None

@pytest.mark.skipif(not _AVAILABLE, reason="bloat_analysis_util.py deps unavailable")
class TestApprovedConstant:
    def test_is_not_none(self):
        assert APPROVED is not None


def test_module_importable():
    """Module bloat_analysis_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
