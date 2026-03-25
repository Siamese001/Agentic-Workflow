"""ADG-driven tests for agentic_core/config/core/agent_defaults_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.config.core.agent_defaults_config  # noqa: F401


def test_module_importable():
    """Module agent_defaults_config must be importable."""
    assert agentic_core.config.core.agent_defaults_config is not None
