"""Foundational behavioral tests for agentic_core/L3_orchestration/reasoning/mcp_manager.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L3_orchestration.reasoning.mcp_manager  # noqa: F401


def test_module_importable():
    """Module mcp_manager must be importable."""
    assert agentic_core.L3_orchestration.reasoning.mcp_manager is not None
