"""ADG-driven tests for agentic_core/L5_safety/enforcement/governance/agent_heal_audit.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L5_safety.enforcement.governance.agent_heal_audit  # noqa: F401


def test_module_importable():
    """Module agent_heal_audit must be importable."""
    assert agentic_core.L5_safety.enforcement.governance.agent_heal_audit is not None
