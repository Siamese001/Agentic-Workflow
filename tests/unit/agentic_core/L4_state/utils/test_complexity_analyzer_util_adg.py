"""ADG-driven tests for agentic_core/L4_state/utils/complexity_analyzer_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L4_state.utils.complexity_analyzer_util  # noqa: F401


def test_module_importable():
    """Module complexity_analyzer_util must be importable."""
    assert agentic_core.L4_state.utils.complexity_analyzer_util is not None
