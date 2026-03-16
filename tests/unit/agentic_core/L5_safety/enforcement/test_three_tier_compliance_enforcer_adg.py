"""ADG-driven tests for L5_safety/enforcement/three_tier_compliance_enforcer.py — fan_in=1."""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_three_tier_compliance_enforcer_adg")
_emit_applies_guardrail("p0", "test_three_tier_compliance_enforcer_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_three_tier_compliance_enforcer_adg", "policy_binding")
_emit_snapshots_state("p0", "test_three_tier_compliance_enforcer_adg", "state_snapshot")
emit_replay_key("p0", "test_three_tier_compliance_enforcer_adg")
emit_determinism_digest("p0", "test_three_tier_compliance_enforcer_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_three_tier_compliance_enforcer_adg", "execution_auth")
_emit_validates_capability("p2", "test_three_tier_compliance_enforcer_adg", "capability_check")
_emit_routes_to_capability("p2", "test_three_tier_compliance_enforcer_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_three_tier_compliance_enforcer_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_three_tier_compliance_enforcer_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_three_tier_compliance_enforcer_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_three_tier_compliance_enforcer_adg", "exec_output")
_emit_dispatches_agent("p3", "test_three_tier_compliance_enforcer_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_three_tier_compliance_enforcer_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_three_tier_compliance_enforcer_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_three_tier_compliance_enforcer_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_three_tier_compliance_enforcer_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_three_tier_compliance_enforcer_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_three_tier_compliance_enforcer_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_three_tier_compliance_enforcer_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_three_tier_compliance_enforcer_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_three_tier_compliance_enforcer_adg", "eval_metric")
_emit_stores_embedding("p4", "test_three_tier_compliance_enforcer_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_three_tier_compliance_enforcer_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_three_tier_compliance_enforcer_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.enforcement.registry_verification_enforcer import AgentInfo
from agentic_core.L5_safety.enforcement.three_tier_compliance_enforcer import (
    CONTRACT_HOOKS,
    GUARDIAN_TEST_PATTERNS,
    AgentCompliance,
    ComplianceResult,
    TierStatus,
)


class TestConstants:
    def test_guardian_test_patterns_list(self):
        assert isinstance(GUARDIAN_TEST_PATTERNS, list)
        assert len(GUARDIAN_TEST_PATTERNS) > 0

    def test_contract_hooks_dict(self):
        assert isinstance(CONTRACT_HOOKS, dict)
        assert "ruff" in CONTRACT_HOOKS


class TestTierStatus:
    def test_creates(self):
        t = TierStatus(tier_name="Contract", is_covered=True)
        assert t.tier_name == "Contract"
        assert t.is_covered is True

    def test_defaults(self):
        t = TierStatus(tier_name="Soul", is_covered=False)
        assert t.coverage_type == ""
        assert t.details == []
        assert t.gaps == []


class TestAgentCompliance:
    def _make_agent_info(self):
        from pathlib import Path
        return AgentInfo(
            class_name="FooAgent",
            file_path=Path("agentic_core/L1_cognition/FooAgent.py"),
            relative_path="agentic_core/L1_cognition/FooAgent.py",
            layer="L1_cognition",
        )

    def test_creates(self):
        ac = AgentCompliance(agent=self._make_agent_info())
        assert ac is not None

    def test_all_uncovered_score_zero(self):
        ac = AgentCompliance(agent=self._make_agent_info())
        assert ac.compliance_score == 0

    def test_one_tier_covered_score_one(self):
        ac = AgentCompliance(agent=self._make_agent_info())
        ac.contract_tier = TierStatus("Contract", is_covered=True)
        assert ac.compliance_score == 1

    def test_fully_compliant_requires_all_three(self):
        ac = AgentCompliance(agent=self._make_agent_info())
        ac.contract_tier = TierStatus("Contract", is_covered=True)
        ac.blueprint_tier = TierStatus("Blueprint", is_covered=True)
        ac.soul_tier = TierStatus("Soul", is_covered=True)
        assert ac.is_fully_compliant is True
        assert ac.compliance_score == 3


class TestComplianceResult:
    def test_creates_with_defaults(self):
        r = ComplianceResult()
        assert r.total_agents == 0
        assert r.fully_compliant == 0
        assert r.agent_compliance == []
