"""ADG-driven tests for agentic_core/L4_state/enforcement/trace_event.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L4_state.enforcement.trace_event  # noqa: F401


def test_module_importable():
    """Module trace_event must be importable."""
    assert agentic_core.L4_state.enforcement.trace_event is not None
