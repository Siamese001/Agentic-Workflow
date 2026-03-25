"""Foundational behavioral tests for agentic_core/agents/agent_registry.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.agents.agent_registry  # noqa: F401


def test_module_importable():
    """Module agent_registry must be importable."""
    assert agentic_core.agents.agent_registry is not None
