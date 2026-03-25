"""ADG-driven tests for agentic_core/L4_state/workflow_engines/redis_cache_client.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L4_state.workflow_engines.redis_cache_client as _mod  # noqa: F401


def test_module_importable():
    """Module redis_cache_client must be importable."""
    assert _mod is not None
