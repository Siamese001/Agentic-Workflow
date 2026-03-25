"""ADG-driven tests for L0_routing/scripts/agent_analysis_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.agent_analysis_config  # noqa: F401


def test_module_importable():
    """Module agent_analysis_config must be importable."""
    assert agentic_core.L0_routing.scripts.agent_analysis_config is not None
