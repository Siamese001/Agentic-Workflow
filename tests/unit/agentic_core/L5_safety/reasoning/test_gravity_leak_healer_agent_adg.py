"""ADG-driven tests for L5_safety/reasoning/GravityLeakHealerAgent.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.reasoning.GravityLeakHealerAgent import GravityLeakHealerAgent


class TestGravityLeakHealerAgent:
    def test_importable(self):
        assert callable(GravityLeakHealerAgent)

    def test_is_class(self):
        assert isinstance(GravityLeakHealerAgent, type)

    def test_has_heal_repository(self):
        assert hasattr(GravityLeakHealerAgent, "heal_repository")

    def test_creates(self):
        agent = GravityLeakHealerAgent()
        assert agent is not None
