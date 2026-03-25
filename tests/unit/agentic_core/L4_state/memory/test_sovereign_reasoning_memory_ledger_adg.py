"""ADG-driven tests for agentic_core/L4_state/memory/sovereign_reasoning_memory_ledger.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L4_state.memory.sovereign_reasoning_memory_ledger  # noqa: F401


def test_module_importable():
    """Module sovereign_reasoning_memory_ledger must be importable."""
    assert agentic_core.L4_state.memory.sovereign_reasoning_memory_ledger is not None
