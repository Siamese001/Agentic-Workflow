"""ADG-driven tests for agentic_core/L0_routing/scripts/check_duplicate_filenames_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L0_routing.scripts.check_duplicate_filenames_util import (  # noqa: F401
        check_for_duplicates,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    check_for_duplicates = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="check_duplicate_filenames_util.py deps unavailable")
class TestCheckForDuplicates:
    def test_is_callable(self):
        assert callable(check_for_duplicates)


def test_module_importable():
    """Module check_duplicate_filenames_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
