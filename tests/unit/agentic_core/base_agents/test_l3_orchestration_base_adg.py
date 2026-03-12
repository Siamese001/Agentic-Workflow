"""ADG-driven tests for base_agents/L3OrchestrationBase.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.base_agents.L3OrchestrationBase import L3OrchestrationBase


class TestL3OrchestrationBase:
    def test_creates(self):
        agent = L3OrchestrationBase()
        assert agent is not None

    def test_default_name(self):
        agent = L3OrchestrationBase()
        assert agent.name == "L3OrchestrationBase"

    def test_default_layer(self):
        agent = L3OrchestrationBase()
        assert agent.layer == "L3"

    def test_has_heal_repository(self):
        assert hasattr(L3OrchestrationBase, "heal_repository")

    def test_is_subclass_of_sovereign_base(self):
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
        assert issubclass(L3OrchestrationBase, SovereignBaseAgent)
