"""ADG-driven tests for L5_safety/reasoning/NeuralAutoImmuneAgent.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.reasoning.NeuralAutoImmuneAgent import NeuralAutoImmuneAgent


class TestNeuralAutoImmuneAgent:
    def test_creates(self):
        agent = NeuralAutoImmuneAgent()
        assert agent is not None

    def test_has_heal(self):
        assert hasattr(NeuralAutoImmuneAgent, "heal")

    def test_has_heal_repository(self):
        assert hasattr(NeuralAutoImmuneAgent, "heal_repository")

    def test_heal_returns_dict(self):
        agent = NeuralAutoImmuneAgent()
        result = agent.heal({"type": "test", "file": "foo.py"})
        assert isinstance(result, dict)
        assert "status" in result
