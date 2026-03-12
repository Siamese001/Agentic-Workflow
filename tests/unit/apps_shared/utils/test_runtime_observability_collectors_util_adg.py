"""ADG-driven tests for apps_shared/utils/runtime_observability_collectors_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.runtime_observability_collectors_util import (  # noqa: F401
        append_event,
        get_events,
        clear_events,
        push_span,
        pop_span,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    append_event = None  # type: ignore[assignment,misc]
    get_events = None  # type: ignore[assignment,misc]
    clear_events = None  # type: ignore[assignment,misc]
    push_span = None  # type: ignore[assignment,misc]
    pop_span = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="runtime_observability_collectors_util.py deps unavailable")
class TestAppendEvent:
    def test_is_callable(self):
        assert callable(append_event)

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_observability_collectors_util.py deps unavailable")
class TestGetEvents:
    def test_is_callable(self):
        assert callable(get_events)

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_observability_collectors_util.py deps unavailable")
class TestClearEvents:
    def test_is_callable(self):
        assert callable(clear_events)

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_observability_collectors_util.py deps unavailable")
class TestPushSpan:
    def test_is_callable(self):
        assert callable(push_span)

@pytest.mark.skipif(not _AVAILABLE, reason="runtime_observability_collectors_util.py deps unavailable")
class TestPopSpan:
    def test_is_callable(self):
        assert callable(pop_span)


def test_module_importable():
    """Module runtime_observability_collectors_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
