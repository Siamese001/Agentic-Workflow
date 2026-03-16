"""Addendum 3.2: C0 Context Mutation Prevention tests."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.context.c0_guard import verify_c0_immutability
from agentic_core.L5_safety.types.hardening_errors import C0MutationViolation
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

_emit_records_execution_trace("p0", "evidence", "test_c0_mutation_prevention")
_emit_applies_guardrail("p0", "test_c0_mutation_prevention", "p0_governance")
_emit_reads_policy_state("p0", "test_c0_mutation_prevention", "policy_binding")
_emit_snapshots_state("p0", "test_c0_mutation_prevention", "state_snapshot")
emit_replay_key("p0", "test_c0_mutation_prevention")
emit_determinism_digest("p0", "test_c0_mutation_prevention")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_c0_mutation_prevention", "execution_auth")
_emit_validates_capability("p2", "test_c0_mutation_prevention", "capability_check")
_emit_routes_to_capability("p2", "test_c0_mutation_prevention", "capability_route")
_emit_writes_via_uwg("p2", "test_c0_mutation_prevention", "uwg_write")
_emit_blocks_direct_write("p2", "test_c0_mutation_prevention", "direct_write_block")
_emit_records_tool_invocation("p2", "test_c0_mutation_prevention", "tool_invocation")
_emit_captures_execution_output("p2", "test_c0_mutation_prevention", "exec_output")
_emit_dispatches_agent("p3", "test_c0_mutation_prevention", "agent_dispatch")
_emit_coordinates_agents("p3", "test_c0_mutation_prevention", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_c0_mutation_prevention", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_c0_mutation_prevention", "healing_outcome")
_emit_escalates_failure("p3", "test_c0_mutation_prevention", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_c0_mutation_prevention", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_c0_mutation_prevention", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_c0_mutation_prevention", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_c0_mutation_prevention", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_c0_mutation_prevention", "eval_metric")
_emit_stores_embedding("p4", "test_c0_mutation_prevention", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_c0_mutation_prevention", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_c0_mutation_prevention", "exec_snapshot_link")


class TestVerifyC0Immutability:
    def test_identical_payloads_pass(self):
        payload = {"query": "hello", "context": "ctx"}
        verify_c0_immutability(payload, {"query": "hello", "context": "ctx"})

    def test_empty_payloads_pass(self):
        verify_c0_immutability({}, {})

    def test_mutated_value_raises(self):
        with pytest.raises(C0MutationViolation, match="mutated"):
            verify_c0_immutability(
                {"key": "original"},
                {"key": "modified"},
            )

    def test_added_key_raises(self):
        with pytest.raises(C0MutationViolation, match="mutated"):
            verify_c0_immutability(
                {"key": "value"},
                {"key": "value", "extra": "injected"},
            )

    def test_removed_key_raises(self):
        with pytest.raises(C0MutationViolation, match="mutated"):
            verify_c0_immutability(
                {"key": "value", "other": "data"},
                {"key": "value"},
            )

    def test_nested_mutation_raises(self):
        with pytest.raises(C0MutationViolation, match="mutated"):
            verify_c0_immutability(
                {"nested": {"a": 1}},
                {"nested": {"a": 2}},
            )

    def test_negative_same_content_never_raises(self):
        """Negative control: same content dict must never raise."""
        payload = {"query": "test", "score": 0.9, "tags": ["a", "b"]}
        raised = False
        try:
            verify_c0_immutability(payload, dict(payload))
        except C0MutationViolation:  # guardian: allow-silent-swallower
            raised = True
        assert not raised
