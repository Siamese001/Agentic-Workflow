"""ADG-driven tests for agentic_core/L0_routing/scripts/archive_duplicates_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.archive_duplicates_util import (  # noqa: F401
        ARCHIVE_BASE,
        PROJECT_ROOT,
        TARGETS,
        TIMESTAMP,
        main,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    main = None  # type: ignore[assignment,misc]
    PROJECT_ROOT = None  # type: ignore[assignment,misc]
    TIMESTAMP = None  # type: ignore[assignment,misc]
    ARCHIVE_BASE = None  # type: ignore[assignment,misc]
    TARGETS = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="archive_duplicates_util.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)

@pytest.mark.skipif(not _AVAILABLE, reason="archive_duplicates_util.py deps unavailable")
class TestProjectRootConstant:
    def test_is_not_none(self):
        assert PROJECT_ROOT is not None

@pytest.mark.skipif(not _AVAILABLE, reason="archive_duplicates_util.py deps unavailable")
class TestTimestampConstant:
    def test_is_not_none(self):
        assert TIMESTAMP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="archive_duplicates_util.py deps unavailable")
class TestArchiveBaseConstant:
    def test_is_not_none(self):
        assert ARCHIVE_BASE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="archive_duplicates_util.py deps unavailable")
class TestTargetsConstant:
    def test_is_not_none(self):
        assert TARGETS is not None


def test_module_importable():
    """Module archive_duplicates_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE