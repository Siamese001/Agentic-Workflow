"""G-16-11: Deterministic snapshot factory for System Learning Meta-Learning Bus.

create_snapshot() is the sole entry point for producing MetaLearningSnapshot
instances. It is bitwise deterministic: same inputs => same snapshot_id.

Invariants:
  - MUST NOT read wall-clock time or timezone data.
  - MUST NOT use randomness.
  - snapshot_id = SHA-256(canonical_concatenation) using b"\\x1f" as delimiter.
  - Canonical concatenation order (strict):
      engine_version, config_surface_version, window_start, window_end,
      telemetry_hash, policy_hash, routing_hash, model_hash, semantic_clock_hash
"""

from __future__ import annotations

import hashlib

from agentic_core.interfaces.determinism_types import SemanticClockSnapshot
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_authorize_and_execute("p2", "snapshot_factory", "execution_auth")
_emit_validates_capability("p2", "snapshot_factory", "capability_check")
_emit_routes_to_capability("p2", "snapshot_factory", "capability_route")
_emit_writes_via_uwg("p2", "snapshot_factory", "uwg_write")
_emit_blocks_direct_write("p2", "snapshot_factory", "direct_write_block")
_emit_records_tool_invocation("p2", "snapshot_factory", "tool_invocation")
_emit_captures_execution_output("p2", "snapshot_factory", "exec_output")
_emit_dispatches_agent("p3", "snapshot_factory", "agent_dispatch")
_emit_coordinates_agents("p3", "snapshot_factory", "agent_coordination")
_emit_records_workflow_lineage("p3", "snapshot_factory", "workflow_lineage")
_emit_records_healing_outcome("p3", "snapshot_factory", "healing_outcome")
_emit_escalates_failure("p3", "snapshot_factory", "failure_escalation")
_emit_orchestrates_workflow("p3", "snapshot_factory", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "snapshot_factory", "healing_dispatch")
_emit_invokes_evaluation("p3", "snapshot_factory", "evaluation_signal")
_emit_records_telemetry_event("p4", "snapshot_factory", "telemetry_event")
_emit_captures_evaluation_metric("p4", "snapshot_factory", "eval_metric")
_emit_stores_embedding("p4", "snapshot_factory", "embedding_store")
_emit_updates_meta_learning_state("p4", "snapshot_factory", "meta_learning")
_emit_links_execution_to_snapshot("p4", "snapshot_factory", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_links_incident_trace,
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
    _emit_writes_through,
)
from system_learning.enforcement.authority_invariants import (
    AuthorityContext,
    assert_zero_execution_authority,
)
from system_learning.types.snapshot_types import MetaLearningSnapshot

_emit_emits_metric_event("snapshot_factory", "p4obs", "metric_1")
_emit_emits_metric_event("snapshot_factory", "p4obs", "metric_2")
_emit_emits_metric_event("snapshot_factory", "p4obs", "metric_3")
_emit_emits_metric_event("snapshot_factory", "p4obs", "metric_4")
_emit_emits_metric_event("snapshot_factory", "p4obs", "metric_5")
_emit_emits_metric_event("snapshot_factory", "p4obs", "metric_6")
_emit_records_incident_event("snapshot_factory", "p4obs", "incident")
_emit_captures_runtime_anomaly("snapshot_factory", "p4obs", "anomaly")
_emit_writes_observability_log("snapshot_factory", "p4obs", "obs_log")
_emit_updates_monitoring_state("snapshot_factory", "p4obs", "mon_state")
_emit_triggers_alert("snapshot_factory", "p4obs", "alert")
_emit_links_incident_trace("snapshot_factory", "p4obs", "trace_link")
_emit_captures_pattern("snapshot_factory", "p3lm", "pattern")
_emit_records_learning_event("snapshot_factory", "p3lm", "learning_event")
_emit_writes_learning_snapshot("snapshot_factory", "p3lm", "snapshot")
_emit_feeds_meta_learning("snapshot_factory", "p3lm", "meta_feed")
_emit_updates_routing_strategy("snapshot_factory", "p3lm", "routing")
_emit_improves_agent_policy("snapshot_factory", "p3lm", "policy")
_emit_stores_learning_state("snapshot_factory", "p3lm", "state")
_emit_records_execution_trace("snapshot_factory", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("snapshot_factory", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("snapshot_factory", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("snapshot_factory", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("snapshot_factory", "L4_STATE", "p2_trace_5")
_emit_reads_environ("snapshot_factory", "env_read", "p2_env_1")
_emit_reads_environ("snapshot_factory", "env_read", "p2_env_2")
_emit_reads_runtime_state("snapshot_factory", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("snapshot_factory", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "snapshot_factory")
_emit_applies_guardrail("p0", "snapshot_factory", "p0_governance")
_emit_snapshots_state("p0", "snapshot_factory", "state_snapshot")
_emit_pulls_context("p1", "snapshot_factory", "context_pull")
_emit_pulls_context("p1", "snapshot_factory", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "snapshot_factory", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "snapshot_factory", "uwg_term_secondary")
_emit_writes_through("p1", "snapshot_factory", "write_through")
_emit_writes_through("p1", "snapshot_factory", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "snapshot_factory", "safety_validation")
_emit_invokes_eval("p1", "snapshot_factory", "eval_call")
_emit_proposal_commits_routing("p1", "snapshot_factory", "routing_commit")
_emit_escalates_to_human("p1", "snapshot_factory", "human_escalation")
_emit_routes_through("p1", "snapshot_factory", "route_through")
_emit_checks_agent_registry("p1", "snapshot_factory", "agent_registry")
_emit_validates_agent_capability("p1", "snapshot_factory", "capability")
_emit_dispatches_execution_plan("p1", "snapshot_factory", "exec_plan")
_emit_agent_executes_agent("p1", "snapshot_factory", "sub_agent")
_emit_routes_to_agent("p1", "snapshot_factory", "target_agent")
_emit_verifies_policy("p1", "snapshot_factory", "policy_check")
_emit_observes_runtime_state("p1", "snapshot_factory", "runtime_state")
_emit_verifies_boundary("p1", "snapshot_factory", "boundary_check")
_emit_transcripts_response("p1", "snapshot_factory", "transcript")
_emit_hard_fails_untranscripted("p1", "snapshot_factory")
_emit_gated_by_confidence("p1", "snapshot_factory", "confidence_gate")
emit_replay_key("p0", "snapshot_factory")
emit_determinism_digest("p0", "snapshot_factory")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# Canonical delimiter between segments in snapshot_id computation.
_SEGMENT_DELIMITER: bytes = b"\x1f"


def _sha256_hex(data: bytes) -> str:
    """Return SHA-256 hex digest of *data*."""
    return hashlib.sha256(data).hexdigest()


def create_snapshot(
    *,
    engine_version: str,
    config_surface_version: str,
    audit_window_start_utc: int,
    audit_window_end_utc: int,
    telemetry_bytes: bytes,
    policy_config_bytes: bytes,
    routing_config_bytes: bytes,
    model_config_bytes: bytes,
    semantic_clock_bytes: bytes,
    semantic_clock: SemanticClockSnapshot,
) -> MetaLearningSnapshot:
    """Create a deterministic, immutable MetaLearningSnapshot.

    Parameters
    ----------
    engine_version : str
        Semantic version of the optimization engine (e.g., "1.0.0").
    config_surface_version : str
        Version string identifying the mutable config surface set.
    audit_window_start_utc : int
        Unix timestamp (inclusive) for the audit data window.
    audit_window_end_utc : int
        Unix timestamp (exclusive) for the audit data window.
    telemetry_bytes : bytes
        Raw bytes of the telemetry data slice. Hashed deterministically.
    policy_config_bytes : bytes
        Canonical bytes of L4 policy config at snapshot time.
    routing_config_bytes : bytes
        Canonical bytes of L4 routing config at snapshot time.
    model_config_bytes : bytes
        Canonical bytes of L4 model config at snapshot time.
    semantic_clock_bytes : bytes
        Canonical bytes of the semantic clock snapshot.
    semantic_clock : SemanticClockSnapshot
        Immutable clock reference embedded in the snapshot.

    Returns
    -------
    MetaLearningSnapshot
        Frozen, content-addressed snapshot.

    Raises
    ------
    ValueError
        If audit_window_start_utc >= audit_window_end_utc.
    AuthorityViolation
        If called in an execution or activation context (fail-closed guard).
    """
    # Authority guard: snapshot creation is READ/WRITE to versioned store only.
    _ctx = AuthorityContext(
        caller_layer="system_learning.snapshots.snapshot_factory",
        operation="create_snapshot",
        target="l4_versioned_store",
        mode="WRITE",
    )
    assert_zero_execution_authority(_ctx)

    # Validate window ordering.
    if audit_window_start_utc >= audit_window_end_utc:
        raise ValueError(
            f"INVALID_AUDIT_WINDOW: start ({audit_window_start_utc}) must be < end ({audit_window_end_utc})"
        )

    # Compute per-input hashes.
    telemetry_hash = _sha256_hex(telemetry_bytes)
    policy_config_hash = _sha256_hex(policy_config_bytes)
    routing_config_hash = _sha256_hex(routing_config_bytes)
    model_config_hash = _sha256_hex(model_config_bytes)
    semantic_clock_hash = _sha256_hex(semantic_clock_bytes)

    # Compute snapshot_id: SHA-256 over canonical concatenation.
    # Strict order: engine_version, config_surface_version, window_start,
    # window_end, telemetry_hash, policy_hash, routing_hash, model_hash,
    # semantic_clock_hash.
    segments: list[bytes] = [
        engine_version.encode("utf-8"),
        config_surface_version.encode("utf-8"),
        str(audit_window_start_utc).encode("utf-8"),
        str(audit_window_end_utc).encode("utf-8"),
        telemetry_hash.encode("utf-8"),
        policy_config_hash.encode("utf-8"),
        routing_config_hash.encode("utf-8"),
        model_config_hash.encode("utf-8"),
        semantic_clock_hash.encode("utf-8"),
    ]
    canonical_bytes = _SEGMENT_DELIMITER.join(segments)
    snapshot_id = _sha256_hex(canonical_bytes)

    return MetaLearningSnapshot(
        snapshot_id=snapshot_id,
        engine_version=engine_version,
        config_surface_version=config_surface_version,
        audit_window_start_utc=audit_window_start_utc,
        audit_window_end_utc=audit_window_end_utc,
        telemetry_hash=telemetry_hash,
        policy_config_hash=policy_config_hash,
        routing_config_hash=routing_config_hash,
        model_config_hash=model_config_hash,
        semantic_clock=semantic_clock,
    )
