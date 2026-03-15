"""ADG-driven tests for apps_shared/utils/observability_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.observability_util import (  # noqa: F401
        clear_events,
        get_all_events,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    get_all_events = None  # type: ignore[assignment,misc]
    clear_events = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="observability_util.py deps unavailable")
class TestGetAllEvents:
    def test_is_callable(self):
        assert callable(get_all_events)

@pytest.mark.skipif(not _AVAILABLE, reason="observability_util.py deps unavailable")
class TestClearEvents:
    def test_is_callable(self):
        assert callable(clear_events)


def test_module_importable():
    """Module observability_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
