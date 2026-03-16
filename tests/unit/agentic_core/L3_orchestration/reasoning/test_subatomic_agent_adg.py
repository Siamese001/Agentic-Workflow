"""ADG-driven tests for agentic_core/L3_orchestration/reasoning/SubAtomicAgent.py — fan_in=2.

Contract tests: SubAtomicAgent init, heal(), heal_repository().
"""
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

_emit_records_execution_trace("p0", "evidence", "test_subatomic_agent_adg")
_emit_applies_guardrail("p0", "test_subatomic_agent_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_subatomic_agent_adg", "policy_binding")
_emit_snapshots_state("p0", "test_subatomic_agent_adg", "state_snapshot")
emit_replay_key("p0", "test_subatomic_agent_adg")
emit_determinism_digest("p0", "test_subatomic_agent_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit

from agentic_core.L3_orchestration.reasoning.SubAtomicAgent import SubAtomicAgent


class TestSubAtomicAgentInit:
    def test_creates_without_args(self):
        agent = SubAtomicAgent()
        assert agent is not None

    def test_is_sovereign_base_agent(self):
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
        assert isinstance(SubAtomicAgent(), SovereignBaseAgent)


class TestSubAtomicAgentHeal:
    def setup_method(self):
        self.agent = SubAtomicAgent()

    def test_heal_returns_dict(self):
        result = self.agent.heal({"type": "NAMING", "file": "foo.py"})
        assert isinstance(result, dict)

    def test_heal_status_skipped(self):
        result = self.agent.heal({"type": "NAMING", "file": "foo.py"})
        assert result["status"] == "skipped"

    def test_heal_has_details(self):
        result = self.agent.heal({})
        assert "details" in result

    def test_heal_has_artifacts_list(self):
        result = self.agent.heal({})
        assert isinstance(result["artifacts"], list)

    def test_heal_has_errors_list(self):
        result = self.agent.heal({})
        assert isinstance(result["errors"], list)


class TestSubAtomicAgentHealRepository:
    def setup_method(self):
        self.agent = SubAtomicAgent()

    def test_heal_repository_returns_dict(self):
        result = self.agent.heal_repository(dry_run=True)
        assert isinstance(result, dict)

    def test_heal_repository_has_skipped(self):
        result = self.agent.heal_repository(dry_run=True)
        assert "skipped" in result

    def test_cycle_detection(self):
        result = self.agent.heal_repository(
            dry_run=True, _call_path={"SubAtomicAgent"}
        )
        assert "cycle_detected" in result or "errors" in result

    def test_depth_limit_respected(self):
        result = self.agent.heal_repository(dry_run=True, depth=99, max_depth=3)
        assert "depth_limited" in result or "errors" in result
