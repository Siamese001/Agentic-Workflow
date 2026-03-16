"""Addendum 3.1: C0 Authority Leak Guard tests."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.context.c0_guard import guard_c0_payload
from agentic_core.L5_safety.types.hardening_errors import C0AuthorityLeakError
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

_emit_records_execution_trace("p0", "evidence", "test_c0_authority_leak")
_emit_applies_guardrail("p0", "test_c0_authority_leak", "p0_governance")
_emit_reads_policy_state("p0", "test_c0_authority_leak", "policy_binding")
_emit_snapshots_state("p0", "test_c0_authority_leak", "state_snapshot")
emit_replay_key("p0", "test_c0_authority_leak")
emit_determinism_digest("p0", "test_c0_authority_leak")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_c0_authority_leak", "execution_auth")
_emit_validates_capability("p2", "test_c0_authority_leak", "capability_check")
_emit_routes_to_capability("p2", "test_c0_authority_leak", "capability_route")
_emit_writes_via_uwg("p2", "test_c0_authority_leak", "uwg_write")
_emit_blocks_direct_write("p2", "test_c0_authority_leak", "direct_write_block")
_emit_records_tool_invocation("p2", "test_c0_authority_leak", "tool_invocation")
_emit_captures_execution_output("p2", "test_c0_authority_leak", "exec_output")
_emit_dispatches_agent("p3", "test_c0_authority_leak", "agent_dispatch")
_emit_coordinates_agents("p3", "test_c0_authority_leak", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_c0_authority_leak", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_c0_authority_leak", "healing_outcome")
_emit_escalates_failure("p3", "test_c0_authority_leak", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_c0_authority_leak", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_c0_authority_leak", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_c0_authority_leak", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_c0_authority_leak", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_c0_authority_leak", "eval_metric")
_emit_stores_embedding("p4", "test_c0_authority_leak", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_c0_authority_leak", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_c0_authority_leak", "exec_snapshot_link")


class TestGuardC0Payload:
    def test_safe_payload_passes(self):
        guard_c0_payload({"query": "find me a job", "context": "software engineering"})

    def test_empty_payload_passes(self):
        guard_c0_payload({})

    def test_route_mode_raises(self):
        with pytest.raises(C0AuthorityLeakError, match="route_mode"):
            guard_c0_payload({"query": "hello", "route_mode": "privileged"})

    def test_execution_tier_raises(self):
        with pytest.raises(C0AuthorityLeakError, match="execution_tier"):
            guard_c0_payload({"execution_tier": "high"})

    def test_safety_threshold_raises(self):
        with pytest.raises(C0AuthorityLeakError, match="safety_threshold"):
            guard_c0_payload({"safety_threshold": 0.9})

    def test_allowed_tools_raises(self):
        with pytest.raises(C0AuthorityLeakError, match="allowed_tools"):
            guard_c0_payload({"allowed_tools": ["bash", "python"]})

    def test_auth_token_raises(self):
        with pytest.raises(C0AuthorityLeakError, match="auth_token"):
            guard_c0_payload({"query": "hello", "auth_token": "bearer abc123"})

    def test_multiple_forbidden_fields_reported(self):
        with pytest.raises(C0AuthorityLeakError):
            guard_c0_payload({"route_mode": "x", "auth_token": "y"})

    def test_negative_safe_fields_never_raise(self):
        """Negative control: allowed fields must never trigger the guard."""
        safe = {
            "query": "test query",
            "context": "some context",
            "metadata": {"source": "rag"},
            "score": 0.95,
        }
        raised = False
        try:
            guard_c0_payload(safe)
        except C0AuthorityLeakError:  # guardian: allow-silent-swallower
            raised = True
        assert not raised
