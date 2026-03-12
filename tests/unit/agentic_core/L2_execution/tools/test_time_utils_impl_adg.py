"""ADG-driven tests for L2_execution/tools/time_utils_impl.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.tools.time_utils_impl import TimeTools


class TestTimeTools:
    def test_creates(self):
        t = TimeTools()
        assert t is not None

    def test_has_fallback_method(self):
        assert callable(getattr(TimeTools, "_get_current_time_fallback", None))
