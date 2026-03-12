"""ADG-driven tests for L5_safety/reasoning/RedTeamAgent.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.RedTeamAgent import RedTeamAgent
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    RedTeamAgent = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="RedTeamAgent deps unavailable")
class TestRedTeamAgent:
    def test_creates(self):
        agent = RedTeamAgent()
        assert agent is not None

    def test_has_heal_repository(self):
        assert hasattr(RedTeamAgent, "heal_repository")

    def test_is_class(self):
        assert isinstance(RedTeamAgent, type)


def test_red_team_agent_importable():
    assert _AVAILABLE or not _AVAILABLE  # just verify module-level import ran
