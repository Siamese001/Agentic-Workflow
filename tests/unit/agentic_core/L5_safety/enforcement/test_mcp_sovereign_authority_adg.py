"""ADG-driven tests for agentic_core/L5_safety/enforcement/mcp_sovereign_authority_enforcer.py — fan_in=2.

Contract tests: MCPSovereignAuthority — breach recording, authorization, tool auditing.
"""
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

_emit_records_execution_trace("p0", "evidence", "test_mcp_sovereign_authority_adg")
_emit_applies_guardrail("p0", "test_mcp_sovereign_authority_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_mcp_sovereign_authority_adg", "policy_binding")
_emit_snapshots_state("p0", "test_mcp_sovereign_authority_adg", "state_snapshot")
emit_replay_key("p0", "test_mcp_sovereign_authority_adg")
emit_determinism_digest("p0", "test_mcp_sovereign_authority_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_mcp_sovereign_authority_adg", "execution_auth")
_emit_validates_capability("p2", "test_mcp_sovereign_authority_adg", "capability_check")
_emit_routes_to_capability("p2", "test_mcp_sovereign_authority_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_mcp_sovereign_authority_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_mcp_sovereign_authority_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_mcp_sovereign_authority_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_mcp_sovereign_authority_adg", "exec_output")
_emit_dispatches_agent("p3", "test_mcp_sovereign_authority_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_mcp_sovereign_authority_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_mcp_sovereign_authority_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_mcp_sovereign_authority_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_mcp_sovereign_authority_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_mcp_sovereign_authority_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_mcp_sovereign_authority_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_mcp_sovereign_authority_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_mcp_sovereign_authority_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_mcp_sovereign_authority_adg", "eval_metric")
_emit_stores_embedding("p4", "test_mcp_sovereign_authority_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_mcp_sovereign_authority_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_mcp_sovereign_authority_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L5_safety.enforcement.mcp_sovereign_authority_enforcer import (
    MCPSovereignAuthority,
    mcp_authority,
)


class TestMCPSovereignAuthorityImport:
    def test_class_importable(self):
        assert callable(MCPSovereignAuthority)

    def test_module_level_instance_exists(self):
        assert isinstance(mcp_authority, MCPSovereignAuthority)


class TestMCPSovereignAuthorityInitialState:
    def test_fresh_instance_authorized(self):
        a = MCPSovereignAuthority()
        assert a.is_authorized() is True

    def test_fresh_violation_count_zero(self):
        a = MCPSovereignAuthority()
        assert a.violation_count == 0

    def test_fresh_breach_log_empty(self):
        a = MCPSovereignAuthority()
        assert a.breach_log == []

    def test_fresh_not_locked(self):
        a = MCPSovereignAuthority()
        assert a.is_locked is False


class TestMCPSovereignAuthorityBreachRecording:
    def test_record_breach_increments_count(self):
        a = MCPSovereignAuthority()
        a.record_breach("test violation")
        assert a.violation_count == 1

    def test_record_breach_adds_to_log(self):
        a = MCPSovereignAuthority()
        a.record_breach("violation A")
        assert len(a.breach_log) == 1
        assert a.breach_log[0]["error"] == "violation A"

    def test_breach_log_entry_has_timestamp(self):
        a = MCPSovereignAuthority()
        a.record_breach("test")
        assert "timestamp" in a.breach_log[0]

    def test_six_breaches_locks_authority(self):
        a = MCPSovereignAuthority()
        for i in range(6):
            a.record_breach(f"breach {i}")
        assert a.is_authorized() is False


class TestMCPSovereignAuthorityAuthorizeToolCall:
    def test_safe_tool_passes(self):
        a = MCPSovereignAuthority()
        a.authorize_tool_call("read_file", {"path": "docs/readme.md"})  # should not raise

    def test_forbidden_sdk_raises_permission_error(self):
        a = MCPSovereignAuthority()
        with pytest.raises(PermissionError, match="Sovereignty Shield"):
            a.authorize_tool_call("openai", {})

    def test_anthropic_sdk_blocked(self):
        a = MCPSovereignAuthority()
        with pytest.raises(PermissionError):
            a.authorize_tool_call("anthropic", {})

    def test_sequential_thinking_within_limit_passes(self):
        a = MCPSovereignAuthority()
        a.authorize_tool_call("sequential_thinking", {"max_steps": 5, "Task": "analyze code"})

    def test_sequential_thinking_over_limit_raises(self):
        a = MCPSovereignAuthority()
        with pytest.raises(ValueError, match="15 steps"):
            a.authorize_tool_call("sequential_thinking", {"max_steps": 20, "Task": "analyze"})
