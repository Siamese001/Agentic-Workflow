"""ADG-driven tests for agentic_core/L0_routing/scripts/fission_executor_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.fission_executor_util  # noqa: F401


def test_module_importable():
    """Module fission_executor_util must be importable."""
    assert agentic_core.L0_routing.scripts.fission_executor_util is not None
