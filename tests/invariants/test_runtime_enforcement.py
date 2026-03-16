"""Addendum Gate A: 5-pair runtime invariant tests (invariant + negative control).

Each pair:
  1. Positive test — invariant passes under correct conditions
  2. Negative test — invariant raises the expected error
"""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.invariants.runtime_invariant_checker import (
    assert_c0_no_authority_fields,
    assert_mutation_in_ledger,
    assert_mutation_source_is_l2,
    assert_state_read_source_is_l4,
    assert_telemetry_no_config_mutation,
)
from agentic_core.L5_safety.types.hardening_errors import (
    C0AuthorityLeakError,
    MutationReplayIntegrityViolation,
    RuntimePolicyMutationViolation,
)
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

_emit_records_execution_trace("p0", "evidence", "test_runtime_enforcement")
_emit_applies_guardrail("p0", "test_runtime_enforcement", "p0_governance")
_emit_reads_policy_state("p0", "test_runtime_enforcement", "policy_binding")
_emit_snapshots_state("p0", "test_runtime_enforcement", "state_snapshot")
emit_replay_key("p0", "test_runtime_enforcement")
emit_determinism_digest("p0", "test_runtime_enforcement")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_runtime_enforcement", "execution_auth")
_emit_validates_capability("p2", "test_runtime_enforcement", "capability_check")
_emit_routes_to_capability("p2", "test_runtime_enforcement", "capability_route")
_emit_writes_via_uwg("p2", "test_runtime_enforcement", "uwg_write")
_emit_blocks_direct_write("p2", "test_runtime_enforcement", "direct_write_block")
_emit_records_tool_invocation("p2", "test_runtime_enforcement", "tool_invocation")
_emit_captures_execution_output("p2", "test_runtime_enforcement", "exec_output")
_emit_dispatches_agent("p3", "test_runtime_enforcement", "agent_dispatch")
_emit_coordinates_agents("p3", "test_runtime_enforcement", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_runtime_enforcement", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_runtime_enforcement", "healing_outcome")
_emit_escalates_failure("p3", "test_runtime_enforcement", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_runtime_enforcement", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_runtime_enforcement", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_runtime_enforcement", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_runtime_enforcement", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_runtime_enforcement", "eval_metric")
_emit_stores_embedding("p4", "test_runtime_enforcement", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_runtime_enforcement", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_runtime_enforcement", "exec_snapshot_link")


class TestInvariant1MutationSourceIsL2:
    def test_positive_l2_accepted(self):
        assert_mutation_source_is_l2("L2_execution")

    def test_negative_non_l2_raises(self):
        with pytest.raises(MutationReplayIntegrityViolation, match="mutation_source"):
            assert_mutation_source_is_l2("L3_manager")


class TestInvariant2MutationInLedger:
    def test_positive_entry_in_ledger(self):
        ledger = [
            {"file_path": "foo/bar.py", "operation": "write"},
        ]
        assert_mutation_in_ledger(ledger, "foo/bar.py", "write")

    def test_negative_missing_entry_raises(self):
        ledger = [{"file_path": "other.py", "operation": "delete"}]
        with pytest.raises(MutationReplayIntegrityViolation, match="mutation not in ledger"):
            assert_mutation_in_ledger(ledger, "foo/bar.py", "write")


class TestInvariant3StateReadSourceIsL4:
    def test_positive_l4_accepted(self):
        assert_state_read_source_is_l4("L4_state")

    def test_negative_non_l4_raises(self):
        with pytest.raises(MutationReplayIntegrityViolation, match="state_read_source"):
            assert_state_read_source_is_l4("L3_cache")


class TestInvariant4C0NoAuthorityFields:
    def test_positive_safe_payload_accepted(self):
        safe_payload = {"query": "find me a job", "context": "software engineering"}
        assert_c0_no_authority_fields(safe_payload)

    def test_negative_authority_field_raises(self):
        bad_payload = {"query": "find jobs", "route_mode": "privileged"}
        with pytest.raises(C0AuthorityLeakError, match="route_mode"):
            assert_c0_no_authority_fields(bad_payload)


class TestInvariant5TelemetryNoConfigMutation:
    def test_positive_stage_s9_allowed(self):
        assert_telemetry_no_config_mutation(current_stage=9, config_mutated=True)

    def test_negative_early_stage_with_mutation_raises(self):
        with pytest.raises(RuntimePolicyMutationViolation, match="stage 3"):
            assert_telemetry_no_config_mutation(current_stage=3, config_mutated=True)

    def test_positive_early_stage_no_mutation_ok(self):
        assert_telemetry_no_config_mutation(current_stage=2, config_mutated=False)
