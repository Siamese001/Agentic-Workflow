"""ADG-driven tests for agentic_core/L2_execution/enforcement/firecracker_manager.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.enforcement.firecracker_manager  # noqa: F401


def test_module_importable():
    """Module firecracker_manager must be importable."""
    assert agentic_core.L2_execution.enforcement.firecracker_manager is not None
