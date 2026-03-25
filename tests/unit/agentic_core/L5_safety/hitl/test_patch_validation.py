"""Addendum 6.1: HITL Patch Validator tests."""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.hitl.patch_validator import ValidatedPatch, validate_patch
from agentic_core.L5_safety.types.hardening_errors import HumanPatchValidationError
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_patch_validation", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_patch_validation", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_patch_validation", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_patch_validation", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_patch_validation", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_patch_validation", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_patch_validation", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_patch_validation", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_patch_validation", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_patch_validation", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_patch_validation", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_patch_validation", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_patch_validation", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_patch_validation", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_patch_validation", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_patch_validation", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_patch_validation", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_patch_validation", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_patch_validation", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_patch_validation", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_patch_validation", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_patch_validation", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_patch_validation", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_patch_validation", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_patch_validation", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_patch_validation", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_patch_validation", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_patch_validation", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_patch_validation")
# REMOVED: _emit_applies_guardrail("p0", "test_patch_validation", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_patch_validation", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_patch_validation", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_patch_validation", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_patch_validation", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_patch_validation", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_patch_validation", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_patch_validation", "write_through")
# REMOVED: _emit_writes_through("p1", "test_patch_validation", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_patch_validation", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_patch_validation", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_patch_validation", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_patch_validation", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_patch_validation", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_patch_validation", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_patch_validation", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_patch_validation", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_patch_validation", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_patch_validation", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_patch_validation", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_patch_validation", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_patch_validation", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_patch_validation", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_patch_validation")
# REMOVED: _emit_gated_by_confidence("p1", "test_patch_validation", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_patch_validation")
# REMOVED: emit_determinism_digest("p0", "test_patch_validation")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_patch_validation", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_patch_validation", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_patch_validation", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_patch_validation", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_patch_validation", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_patch_validation", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_patch_validation", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_patch_validation", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_patch_validation", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_patch_validation", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_patch_validation", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_patch_validation", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_patch_validation", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_patch_validation", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_patch_validation", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_patch_validation", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_patch_validation", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_patch_validation", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_patch_validation", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_patch_validation", "exec_snapshot_link")


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class TestValidatePatch:
    def _valid_patch(self) -> dict:
        return {
            "original_plan_hash": "abc123",
            "structured_patch_schema": {"type": "MODIFY_DIFF", "file": "foo.py"},
            "reviewer_signature": "reviewer@example.com",
        }

    def test_valid_patch_returns_validated(self):
        result = validate_patch(self._valid_patch())
        assert isinstance(result, ValidatedPatch)
        assert result.reviewer_signature == "reviewer@example.com"
        assert result.original_plan_hash == "abc123"
        assert result.patch_hash  # non-empty SHA256

    def test_patch_hash_is_64_chars(self):
        result = validate_patch(self._valid_patch())
        assert len(result.patch_hash) == 64

    def test_missing_reviewer_signature_raises(self):
        patch = self._valid_patch()
        del patch["reviewer_signature"]
        with pytest.raises(HumanPatchValidationError, match="reviewer_signature"):
            validate_patch(patch)

    def test_missing_plan_hash_raises(self):
        patch = self._valid_patch()
        del patch["original_plan_hash"]
        with pytest.raises(HumanPatchValidationError, match="original_plan_hash"):
            validate_patch(patch)

    def test_missing_patch_schema_raises(self):
        patch = self._valid_patch()
        del patch["structured_patch_schema"]
        with pytest.raises(HumanPatchValidationError, match="structured_patch_schema"):
            validate_patch(patch)

    def test_empty_reviewer_signature_raises(self):
        patch = self._valid_patch()
        patch["reviewer_signature"] = ""
        with pytest.raises(HumanPatchValidationError, match="reviewer_signature"):
            validate_patch(patch)

    def test_empty_dict_raises(self):
        with pytest.raises(HumanPatchValidationError):
            validate_patch({})

    def test_different_patches_different_hashes(self):
        p1 = self._valid_patch()
        p2 = dict(self._valid_patch())
        p2["reviewer_signature"] = "other@example.com"
        r1 = validate_patch(p1)
        r2 = validate_patch(p2)
        assert r1.patch_hash != r2.patch_hash

    def test_negative_complete_patch_never_raises(self):
        """Negative control: all fields present must never raise."""
        raised = False
        try:
            validate_patch(self._valid_patch())
        with pytest.raises(HumanPatchValidationError):
            raised = True
        assert not raised
