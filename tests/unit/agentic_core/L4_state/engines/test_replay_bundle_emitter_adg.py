"""ADG-driven tests for agentic_core/L4_state/engines/replay_bundle_emitter.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L4_state.engines.replay_bundle_emitter  # noqa: F401


def test_module_importable():
    """Module replay_bundle_emitter must be importable."""
    assert agentic_core.L4_state.engines.replay_bundle_emitter is not None
