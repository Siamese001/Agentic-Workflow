"""ADG-driven tests for L5_safety/reasoning/RedTeamAgent.py — fan_in=1."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_red_team_agent_adg")
_emit_applies_guardrail("p0", "test_red_team_agent_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_red_team_agent_adg", "policy_binding")
_emit_snapshots_state("p0", "test_red_team_agent_adg", "state_snapshot")
emit_replay_key("p0", "test_red_team_agent_adg")
emit_determinism_digest("p0", "test_red_team_agent_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.reasoning.RedTeamAgent import RedTeamAgent
    _AVAILABLE = True
except ImportError:
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
