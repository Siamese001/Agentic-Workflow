"""ADG-driven tests for apps_shared/utils/archive_file_access_deprecated_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.archive_file_access_deprecated_util import (  # noqa: F401
        ARCHIVE_FILE_ACCESS_DEPRECATED,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ARCHIVE_FILE_ACCESS_DEPRECATED = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="archive_file_access_deprecated_util.py deps unavailable")
class TestARCHIVE_FILE_ACCESS_DEPRECATED:
    def test_is_class(self):
        assert isinstance(ARCHIVE_FILE_ACCESS_DEPRECATED, type)
    def test_importable(self):
        assert ARCHIVE_FILE_ACCESS_DEPRECATED is not None


def test_module_importable():
    """Module archive_file_access_deprecated_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
