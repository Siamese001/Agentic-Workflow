"""ADG-driven tests for agentic_core/L0_routing/scripts/run_guardian_hierarchy_compliance.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L0_routing.scripts.run_guardian_hierarchy_compliance  # noqa: F401


def test_module_importable():
    """Module run_guardian_hierarchy_compliance must be importable."""
    assert agentic_core.L0_routing.scripts.run_guardian_hierarchy_compliance is not None
