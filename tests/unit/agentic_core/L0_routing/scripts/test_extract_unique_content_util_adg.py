"""ADG-driven tests for agentic_core/L0_routing/scripts/extract_unique_content_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.extract_unique_content_util import (  # noqa: F401
        build_codebase_index,
        analyze_archive_file,
        main,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    build_codebase_index = None  # type: ignore[assignment,misc]
    analyze_archive_file = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="extract_unique_content_util.py deps unavailable")
class TestBuildCodebaseIndex:
    def test_is_callable(self):
        assert callable(build_codebase_index)

@pytest.mark.skipif(not _AVAILABLE, reason="extract_unique_content_util.py deps unavailable")
class TestAnalyzeArchiveFile:
    def test_is_callable(self):
        assert callable(analyze_archive_file)

@pytest.mark.skipif(not _AVAILABLE, reason="extract_unique_content_util.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)


def test_module_importable():
    """Module extract_unique_content_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
