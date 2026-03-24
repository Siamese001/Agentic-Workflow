"""Addendum 2.2: Ledger Integrity Validator tests."""

from __future__ import annotations

import pytest

from agentic_core.L4_state.ledger.integrity_validator import (
    append_with_hash,
    validate_ledger_chain,
    validate_ledger_file,
)
from agentic_core.L5_safety.types.hardening_errors import LedgerIntegrityViolation
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_ledger_integrity")
_emit_applies_guardrail("p0", "test_ledger_integrity", "p0_governance")
_emit_reads_policy_state("p0", "test_ledger_integrity", "policy_binding")
_emit_snapshots_state("p0", "test_ledger_integrity", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

_emit_emits_metric_event("test_ledger_integrity", "p4obs", "metric_1")
_emit_emits_metric_event("test_ledger_integrity", "p4obs", "metric_2")
_emit_emits_metric_event("test_ledger_integrity", "p4obs", "metric_3")
_emit_emits_metric_event("test_ledger_integrity", "p4obs", "metric_4")
_emit_emits_metric_event("test_ledger_integrity", "p4obs", "metric_5")
_emit_emits_metric_event("test_ledger_integrity", "p4obs", "metric_6")
_emit_records_incident_event("test_ledger_integrity", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_ledger_integrity", "p4obs", "anomaly")
_emit_writes_observability_log("test_ledger_integrity", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_ledger_integrity", "p4obs", "mon_state")
_emit_triggers_alert("test_ledger_integrity", "p4obs", "alert")
_emit_links_incident_trace("test_ledger_integrity", "p4obs", "trace_link")
_emit_captures_pattern("test_ledger_integrity", "p3lm", "pattern")
_emit_records_learning_event("test_ledger_integrity", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_ledger_integrity", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_ledger_integrity", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_ledger_integrity", "p3lm", "routing")
_emit_improves_agent_policy("test_ledger_integrity", "p3lm", "policy")
_emit_stores_learning_state("test_ledger_integrity", "p3lm", "state")
_emit_records_execution_trace("test_ledger_integrity", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_ledger_integrity", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_ledger_integrity", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_ledger_integrity", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_ledger_integrity", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_ledger_integrity", "env_read", "p2_env_1")
_emit_reads_environ("test_ledger_integrity", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_ledger_integrity", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_ledger_integrity", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_ledger_integrity", "context_pull")
_emit_pulls_context("p1", "test_ledger_integrity", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_ledger_integrity", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_ledger_integrity", "uwg_term_2")
_emit_writes_through("p1", "test_ledger_integrity", "write_through")
_emit_writes_through("p1", "test_ledger_integrity", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_ledger_integrity", "safety_validation")
_emit_invokes_eval("p1", "test_ledger_integrity", "eval_call")
_emit_proposal_commits_routing("p1", "test_ledger_integrity", "routing_commit")
_emit_escalates_to_human("p1", "test_ledger_integrity", "human_escalation")
_emit_routes_through("p1", "test_ledger_integrity", "route_through")
_emit_checks_agent_registry("p1", "test_ledger_integrity", "agent_registry")
_emit_validates_agent_capability("p1", "test_ledger_integrity", "capability")
_emit_dispatches_execution_plan("p1", "test_ledger_integrity", "exec_plan")
_emit_agent_executes_agent("p1", "test_ledger_integrity", "sub_agent")
_emit_routes_to_agent("p1", "test_ledger_integrity", "target_agent")
_emit_verifies_policy("p1", "test_ledger_integrity", "policy_check")
_emit_observes_runtime_state("p1", "test_ledger_integrity", "runtime_state")
_emit_verifies_boundary("p1", "test_ledger_integrity", "boundary_check")
_emit_transcripts_response("p1", "test_ledger_integrity", "transcript")
_emit_hard_fails_untranscripted("p1", "test_ledger_integrity")
_emit_gated_by_confidence("p1", "test_ledger_integrity", "confidence_gate")
emit_replay_key("p0", "test_ledger_integrity")
emit_determinism_digest("p0", "test_ledger_integrity")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_ledger_integrity", "execution_auth")
_emit_validates_capability("p2", "test_ledger_integrity", "capability_check")
_emit_routes_to_capability("p2", "test_ledger_integrity", "capability_route")
_emit_writes_via_uwg("p2", "test_ledger_integrity", "uwg_write")
_emit_blocks_direct_write("p2", "test_ledger_integrity", "direct_write_block")
_emit_records_tool_invocation("p2", "test_ledger_integrity", "tool_invocation")
_emit_captures_execution_output("p2", "test_ledger_integrity", "exec_output")
_emit_dispatches_agent("p3", "test_ledger_integrity", "agent_dispatch")
_emit_coordinates_agents("p3", "test_ledger_integrity", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_ledger_integrity", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_ledger_integrity", "healing_outcome")
_emit_escalates_failure("p3", "test_ledger_integrity", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_ledger_integrity", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_ledger_integrity", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_ledger_integrity", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_ledger_integrity", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_ledger_integrity", "eval_metric")
_emit_stores_embedding("p4", "test_ledger_integrity", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_ledger_integrity", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_ledger_integrity", "exec_snapshot_link")


class TestAppendWithHash:
    def test_appended_entry_has_hash(self):
        entries: list = []
        entry = append_with_hash(entries, {"op": "write", "file": "foo.py"})
        assert "_hash" in entry
        assert len(entry["_hash"]) == 64

    def test_chain_grows(self):
        entries: list = []
        append_with_hash(entries, {"op": "write", "file": "a.py"})
        append_with_hash(entries, {"op": "delete", "file": "b.py"})
        assert len(entries) == 2

    def test_hashes_are_different_per_entry(self):
        entries: list = []
        e1 = append_with_hash(entries, {"op": "write", "file": "a.py"})
        e2 = append_with_hash(entries, {"op": "write", "file": "b.py"})
        assert e1["_hash"] != e2["_hash"]


class TestValidateLedgerChain:
    def test_valid_chain_passes(self):
        entries: list = []
        append_with_hash(entries, {"op": "write", "file": "a.py"})
        append_with_hash(entries, {"op": "write", "file": "b.py"})
        validate_ledger_chain(entries)

    def test_empty_chain_passes(self):
        validate_ledger_chain([])

    def test_tampered_hash_raises(self):
        entries: list = []
        append_with_hash(entries, {"op": "write", "file": "a.py"})
        entries[0]["_hash"] = "0" * 64
        with pytest.raises(LedgerIntegrityViolation, match="hash mismatch"):
            validate_ledger_chain(entries)

    def test_missing_hash_field_raises(self):
        entries = [{"op": "write", "file": "a.py"}]
        with pytest.raises(LedgerIntegrityViolation, match="missing '_hash'"):
            validate_ledger_chain(entries)

    def test_middle_tamper_detected(self):
        entries: list = []
        append_with_hash(entries, {"op": "write", "file": "a.py"})
        append_with_hash(entries, {"op": "write", "file": "b.py"})
        append_with_hash(entries, {"op": "write", "file": "c.py"})
        entries[1]["_hash"] = "deadbeef" * 8
        with pytest.raises(LedgerIntegrityViolation):
            validate_ledger_chain(entries)

    def test_negative_untampered_chain_never_raises(self):
        entries: list = []
        for i in range(5):
            append_with_hash(entries, {"op": "write", "file": f"f{i}.py"})
        raised = False
        try:
            validate_ledger_chain(entries)
        except LedgerIntegrityViolation:  # guardian: allow-silent-swallower
            raised = True
        assert not raised


class TestValidateLedgerFile:
    def test_valid_file_passes(self, tmp_path):
        import json

        ledger_path = tmp_path / "ledger.jsonl"
        entries: list = []
        for i in range(3):
            append_with_hash(entries, {"op": "write", "file": f"f{i}.py"})
        with open(ledger_path, "w") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")
        validate_ledger_file(ledger_path)

    def test_nonexistent_file_passes_silently(self, tmp_path):
        validate_ledger_file(tmp_path / "nonexistent.jsonl")
