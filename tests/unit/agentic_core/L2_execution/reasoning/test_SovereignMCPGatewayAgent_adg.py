"""ADG-driven tests for agentic_core/L2_execution/reasoning/SovereignMCPGatewayAgent.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.reasoning.SovereignMCPGatewayAgent  # noqa: F401


def test_module_importable():
    """Module SovereignMCPGatewayAgent must be importable."""
    assert agentic_core.L2_execution.reasoning.SovereignMCPGatewayAgent is not None
