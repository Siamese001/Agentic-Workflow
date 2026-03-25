"""ADG-driven tests for agentic_core/L2_execution/tools/tool_chain_executor.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.tools.tool_chain_executor  # noqa: F401


def test_module_importable():
    """Module tool_chain_executor must be importable."""
    assert agentic_core.L2_execution.tools.tool_chain_executor is not None
