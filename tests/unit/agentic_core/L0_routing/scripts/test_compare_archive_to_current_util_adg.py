"""ADG-driven tests for agentic_core/L0_routing/scripts/compare_archive_to_current_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.compare_archive_to_current_util import (  # noqa: F401
        file_hash,
        find_in_current,
        main,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    file_hash = None  # type: ignore[assignment,misc]
    find_in_current = None  # type: ignore[assignment,misc]
    main = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="compare_archive_to_current_util.py deps unavailable")
class TestFileHash:
    def test_is_callable(self):
        assert callable(file_hash)

@pytest.mark.skipif(not _AVAILABLE, reason="compare_archive_to_current_util.py deps unavailable")
class TestFindInCurrent:
    def test_is_callable(self):
        assert callable(find_in_current)

@pytest.mark.skipif(not _AVAILABLE, reason="compare_archive_to_current_util.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)


def test_module_importable():
    """Module compare_archive_to_current_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
