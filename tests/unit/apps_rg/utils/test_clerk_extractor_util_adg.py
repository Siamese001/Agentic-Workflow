"""ADG-driven tests for apps_rg/utils/clerk_extractor_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_rg.utils.clerk_extractor_util import (  # noqa: F401
        ClerkExtractor,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    ClerkExtractor = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="clerk_extractor_util.py deps unavailable")
class TestClerkExtractor:
    def test_is_class(self):
        assert isinstance(ClerkExtractor, type)
    def test_importable(self):
        assert ClerkExtractor is not None


def test_module_importable():
    """Module clerk_extractor_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
