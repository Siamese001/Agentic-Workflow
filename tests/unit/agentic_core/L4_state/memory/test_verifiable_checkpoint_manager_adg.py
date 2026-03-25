"""ADG-driven tests for agentic_core/L4_state/memory/verifiable_checkpoint_manager.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L4_state.memory.verifiable_checkpoint_manager  # noqa: F401


def test_module_importable():
    """Module verifiable_checkpoint_manager must be importable."""
    assert agentic_core.L4_state.memory.verifiable_checkpoint_manager is not None
