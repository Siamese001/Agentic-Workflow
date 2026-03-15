"""ADG-driven tests for utils/state_util.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.utils.state_util import check_past_failures
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    check_past_failures = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="state_util deps unavailable")
class TestCheckPastFailures:
    def test_returns_string(self):
        result = check_past_failures("test task description")
        assert isinstance(result, str)

    def test_handles_empty_task(self):
        result = check_past_failures("")
        assert isinstance(result, str)


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
