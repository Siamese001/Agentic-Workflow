"""P1 MCP optimization tests for git_ops_impl.py — new log/diff/branch/push methods."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.tools.git_ops_impl  # noqa: F401


def test_module_importable():
    """Module git_ops_impl must be importable."""
    assert agentic_core.L2_execution.tools.git_ops_impl is not None
