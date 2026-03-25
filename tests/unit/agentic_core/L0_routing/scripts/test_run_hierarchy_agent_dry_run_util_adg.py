"""ADG-driven tests for agentic_core/L0_routing/scripts/run_hierarchy_agent_dry_run_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.run_hierarchy_agent_dry_run_util  # noqa: F401


def test_module_importable():
    """Module run_hierarchy_agent_dry_run_util must be importable."""
    assert agentic_core.L0_routing.scripts.run_hierarchy_agent_dry_run_util is not None
