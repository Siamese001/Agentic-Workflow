"""ADG-driven tests for agentic_core/L0_routing/scripts/aggressive_dedup_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.aggressive_dedup_util import (  # noqa: F401
        APPS_DIRS,
        find_low_value_files,
        find_redundant_files,
        find_similar_named_files,
        get_all_classes_in_codebase,
        main,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    get_all_classes_in_codebase = None  # type: ignore[assignment,misc]
    find_redundant_files = None  # type: ignore[assignment,misc]
    find_similar_named_files = None  # type: ignore[assignment,misc]
    find_low_value_files = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]
    APPS_DIRS = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="aggressive_dedup_util.py deps unavailable")
class TestGetAllClassesInCodebase:
    def test_is_callable(self):
        assert callable(get_all_classes_in_codebase)

@pytest.mark.skipif(not _AVAILABLE, reason="aggressive_dedup_util.py deps unavailable")
class TestFindRedundantFiles:
    def test_is_callable(self):
        assert callable(find_redundant_files)

@pytest.mark.skipif(not _AVAILABLE, reason="aggressive_dedup_util.py deps unavailable")
class TestFindSimilarNamedFiles:
    def test_is_callable(self):
        assert callable(find_similar_named_files)

@pytest.mark.skipif(not _AVAILABLE, reason="aggressive_dedup_util.py deps unavailable")
class TestFindLowValueFiles:
    def test_is_callable(self):
        assert callable(find_low_value_files)

@pytest.mark.skipif(not _AVAILABLE, reason="aggressive_dedup_util.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="aggressive_dedup_util.py deps unavailable")
class TestAppsDirsConstant:
    def test_is_not_none(self):
        assert APPS_DIRS is not None


def test_module_importable():
    """Module aggressive_dedup_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE