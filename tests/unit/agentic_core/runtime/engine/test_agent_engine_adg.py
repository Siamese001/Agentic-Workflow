"""ADG-driven tests for agentic_core/runtime/engine/agent_engine.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.runtime.engine.agent_engine  # noqa: F401


def test_module_importable():
    """Module agent_engine must be importable."""
    assert agentic_core.runtime.engine.agent_engine is not None
