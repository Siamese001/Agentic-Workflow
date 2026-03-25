"""ADG-driven tests for L2_execution/engines/execute_command_executor.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.engines.execute_command_executor  # noqa: F401


def test_module_importable():
    """Module execute_command_executor must be importable."""
    assert agentic_core.L2_execution.engines.execute_command_executor is not None
