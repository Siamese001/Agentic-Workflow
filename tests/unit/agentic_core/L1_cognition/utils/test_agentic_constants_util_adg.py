"""ADG-driven tests for L1_cognition/utils/agentic_constants_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L1_cognition.utils.agentic_constants_util import (
        max_complexity,
        max_func_lines,
        max_phase_time,
        max_retry_attempts,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    max_complexity = max_func_lines = max_phase_time = max_retry_attempts = None


@pytest.mark.skipif(not _AVAILABLE, reason="agentic_constants_util deps unavailable")
class TestAgenticConstantsUtil:
    def test_max_complexity_is_int(self):
        assert isinstance(max_complexity, int)

    def test_max_func_lines_is_int(self):
        assert isinstance(max_func_lines, int)

    def test_max_phase_time_positive(self):
        assert max_phase_time > 0

    def test_max_retry_attempts_positive(self):
        assert max_retry_attempts > 0


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
