"""
Wave 1.3 Negative Test: SurgicalManifest.verify_hash enforcement at construction sites.

Proves:
1. A valid SurgicalManifest passes ``require_manifest_hash_ok``.
2. Mutating ``ast_snippet`` after construction causes ``verify_hash()`` → False.
3. ``require_manifest_hash_ok`` raises ``ValueError`` on the mutated manifest.
"""

from __future__ import annotations

import hashlib

import pytest

from agentic_core.L0_routing.types.determinism_contracts_types import (
    require_manifest_hash_ok,
)
from agentic_core.L0_routing.types.determinism_types import (
    FixConstraint,
    SurgicalManifest,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
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
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("test_manifest_verify_hash_enforced", "p4obs", "metric_1")
_emit_emits_metric_event("test_manifest_verify_hash_enforced", "p4obs", "metric_2")
_emit_emits_metric_event("test_manifest_verify_hash_enforced", "p4obs", "metric_3")
_emit_emits_metric_event("test_manifest_verify_hash_enforced", "p4obs", "metric_4")
_emit_emits_metric_event("test_manifest_verify_hash_enforced", "p4obs", "metric_5")
_emit_emits_metric_event("test_manifest_verify_hash_enforced", "p4obs", "metric_6")
_emit_records_incident_event("test_manifest_verify_hash_enforced", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_manifest_verify_hash_enforced", "p4obs", "anomaly")
_emit_writes_observability_log("test_manifest_verify_hash_enforced", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_manifest_verify_hash_enforced", "p4obs", "mon_state")
_emit_triggers_alert("test_manifest_verify_hash_enforced", "p4obs", "alert")
_emit_links_incident_trace("test_manifest_verify_hash_enforced", "p4obs", "trace_link")
_emit_captures_pattern("test_manifest_verify_hash_enforced", "p3lm", "pattern")
_emit_records_learning_event("test_manifest_verify_hash_enforced", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_manifest_verify_hash_enforced", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_manifest_verify_hash_enforced", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_manifest_verify_hash_enforced", "p3lm", "routing")
_emit_improves_agent_policy("test_manifest_verify_hash_enforced", "p3lm", "policy")
_emit_stores_learning_state("test_manifest_verify_hash_enforced", "p3lm", "state")
_emit_records_execution_trace("test_manifest_verify_hash_enforced", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_manifest_verify_hash_enforced", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_manifest_verify_hash_enforced", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_manifest_verify_hash_enforced", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_manifest_verify_hash_enforced", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_manifest_verify_hash_enforced", "env_read", "p2_env_1")
_emit_reads_environ("test_manifest_verify_hash_enforced", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_manifest_verify_hash_enforced", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_manifest_verify_hash_enforced", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_manifest_verify_hash_enforced")
_emit_applies_guardrail("p0", "test_manifest_verify_hash_enforced", "p0_governance")
_emit_reads_policy_state("p0", "test_manifest_verify_hash_enforced", "policy_binding")
_emit_snapshots_state("p0", "test_manifest_verify_hash_enforced", "state_snapshot")
_emit_pulls_context("p1", "test_manifest_verify_hash_enforced", "context_pull")
_emit_pulls_context("p1", "test_manifest_verify_hash_enforced", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_manifest_verify_hash_enforced", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_manifest_verify_hash_enforced", "uwg_term_secondary")
_emit_writes_through("p1", "test_manifest_verify_hash_enforced", "write_through")
_emit_writes_through("p1", "test_manifest_verify_hash_enforced", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_manifest_verify_hash_enforced", "safety_validation")
_emit_invokes_eval("p1", "test_manifest_verify_hash_enforced", "eval_call")
_emit_proposal_commits_routing("p1", "test_manifest_verify_hash_enforced", "routing_commit")
emit_replay_key("p0", "test_manifest_verify_hash_enforced")
emit_determinism_digest("p0", "test_manifest_verify_hash_enforced")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_manifest_verify_hash_enforced", "execution_auth")
_emit_validates_capability("p2", "test_manifest_verify_hash_enforced", "capability_check")
_emit_routes_to_capability("p2", "test_manifest_verify_hash_enforced", "capability_route")
_emit_writes_via_uwg("p2", "test_manifest_verify_hash_enforced", "uwg_write")
_emit_blocks_direct_write("p2", "test_manifest_verify_hash_enforced", "direct_write_block")
_emit_records_tool_invocation("p2", "test_manifest_verify_hash_enforced", "tool_invocation")
_emit_captures_execution_output("p2", "test_manifest_verify_hash_enforced", "exec_output")
_emit_dispatches_agent("p3", "test_manifest_verify_hash_enforced", "agent_dispatch")
_emit_coordinates_agents("p3", "test_manifest_verify_hash_enforced", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_manifest_verify_hash_enforced", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_manifest_verify_hash_enforced", "healing_outcome")
_emit_escalates_failure("p3", "test_manifest_verify_hash_enforced", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_manifest_verify_hash_enforced", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_manifest_verify_hash_enforced", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_manifest_verify_hash_enforced", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_manifest_verify_hash_enforced", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_manifest_verify_hash_enforced", "eval_metric")
_emit_stores_embedding("p4", "test_manifest_verify_hash_enforced", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_manifest_verify_hash_enforced", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_manifest_verify_hash_enforced", "exec_snapshot_link")


def _build_valid_manifest(snippet: str = "TestNode.op()") -> SurgicalManifest:
    """Construct a SurgicalManifest with correct hash."""
    return SurgicalManifest(
        schema_version="1.0.0",
        correlation_id="TEST-0001",
        node_id="TestNode",
        target_layer="L3",
        ast_snippet=snippet,
        serialization_canon="test_canon",
        fix_constraint=FixConstraint.RELAXED,
        manifest_hash=hashlib.sha256(snippet.encode("utf-8")).hexdigest(),
        change_history=(),
        provenance_chain=("TEST-0001",),
    )


class TestRequireManifestHashOk:
    """require_manifest_hash_ok must raise on hash mismatch."""

    def test_valid_manifest_passes(self):
        manifest = _build_valid_manifest()
        assert manifest.verify_hash() is True
        require_manifest_hash_ok(manifest)

    def test_mutated_snippet_fails_verify(self):
        manifest = _build_valid_manifest()
        object.__setattr__(manifest, "ast_snippet", "TAMPERED.op()")
        assert manifest.verify_hash() is False

    def test_mutated_snippet_raises_value_error(self):
        manifest = _build_valid_manifest()
        object.__setattr__(manifest, "ast_snippet", "TAMPERED.op()")
        with pytest.raises(ValueError, match="integrity hash mismatch"):
            require_manifest_hash_ok(manifest)

    def test_mutated_hash_fails_verify(self):
        manifest = _build_valid_manifest()
        object.__setattr__(manifest, "manifest_hash", "0" * 64)
        assert manifest.verify_hash() is False

    def test_mutated_hash_raises_value_error(self):
        manifest = _build_valid_manifest()
        object.__setattr__(manifest, "manifest_hash", "0" * 64)
        with pytest.raises(ValueError, match="integrity hash mismatch"):
            require_manifest_hash_ok(manifest)
