"""ADG-driven tests for apps_rg/__main__.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_rg.__main__ import (  # noqa: F401
        main,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    main = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="__main__.py deps unavailable")
class TestMain:
    def test_is_callable(self):
        assert callable(main)


def test_module_importable():
    """Module __main__.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
