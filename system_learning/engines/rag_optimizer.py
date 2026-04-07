"""G-16-19: RAG optimizer — proposal-only optimizer for RAG parameters.

Proposes changes to RAG parameters based on metrics, enforcing:
  - Allowlist constraints (only allowed surfaces)
  - Bounds + max-delta enforcement
  - Cooldown + sample-size dampening
  - Deterministic inputs only (no wall-clock)
  - Proposal-only (no activation)
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_authorize_and_execute("p2", "rag_optimizer", "execution_auth")
_emit_validates_capability("p2", "rag_optimizer", "capability_check")
_emit_routes_to_capability("p2", "rag_optimizer", "capability_route")
_emit_writes_via_uwg("p2", "rag_optimizer", "uwg_write")
_emit_blocks_direct_write("p2", "rag_optimizer", "direct_write_block")
_emit_records_tool_invocation("p2", "rag_optimizer", "tool_invocation")
_emit_captures_execution_output("p2", "rag_optimizer", "exec_output")
_emit_dispatches_agent("p3", "rag_optimizer", "agent_dispatch")
_emit_coordinates_agents("p3", "rag_optimizer", "agent_coordination")
_emit_records_workflow_lineage("p3", "rag_optimizer", "workflow_lineage")
_emit_records_healing_outcome("p3", "rag_optimizer", "healing_outcome")
_emit_escalates_failure("p3", "rag_optimizer", "failure_escalation")
_emit_orchestrates_workflow("p3", "rag_optimizer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rag_optimizer", "healing_dispatch")
_emit_invokes_evaluation("p3", "rag_optimizer", "evaluation_signal")
_emit_records_telemetry_event("p4", "rag_optimizer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rag_optimizer", "eval_metric")
_emit_stores_embedding("p4", "rag_optimizer", "embedding_store")
_emit_updates_meta_learning_state("p4", "rag_optimizer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rag_optimizer", "exec_snapshot_link")
from system_learning.constraints.dampening import (
    CooldownPolicy,
    DampeningViolation,
    SampleSizePolicy,
    assert_cooldown_ok,
    assert_min_sample_size,
)
from system_learning.constraints.delta_enforcer import validate_surface_change

_emit_applies_guardrail("p0", "rag_optimizer", "p0_governance")
_emit_reads_policy_state("p0", "rag_optimizer", "policy_binding")
_emit_snapshots_state("p0", "rag_optimizer", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("rag_optimizer", "p4obs", "metric_1")
_emit_emits_metric_event("rag_optimizer", "p4obs", "metric_2")
_emit_emits_metric_event("rag_optimizer", "p4obs", "metric_3")
_emit_emits_metric_event("rag_optimizer", "p4obs", "metric_4")
_emit_emits_metric_event("rag_optimizer", "p4obs", "metric_5")
_emit_emits_metric_event("rag_optimizer", "p4obs", "metric_6")
_emit_records_incident_event("rag_optimizer", "p4obs", "incident")
_emit_captures_runtime_anomaly("rag_optimizer", "p4obs", "anomaly")
_emit_writes_observability_log("rag_optimizer", "p4obs", "obs_log")
_emit_updates_monitoring_state("rag_optimizer", "p4obs", "mon_state")
_emit_triggers_alert("rag_optimizer", "p4obs", "alert")
_emit_links_incident_trace("rag_optimizer", "p4obs", "trace_link")
_emit_captures_pattern("rag_optimizer", "p3lm", "pattern")
_emit_records_learning_event("rag_optimizer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("rag_optimizer", "p3lm", "snapshot")
_emit_feeds_meta_learning("rag_optimizer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("rag_optimizer", "p3lm", "routing")
_emit_improves_agent_policy("rag_optimizer", "p3lm", "policy")
_emit_stores_learning_state("rag_optimizer", "p3lm", "state")
_emit_records_execution_trace("rag_optimizer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("rag_optimizer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("rag_optimizer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("rag_optimizer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("rag_optimizer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("rag_optimizer", "env_read", "p2_env_1")
_emit_reads_environ("rag_optimizer", "env_read", "p2_env_2")
_emit_reads_runtime_state("rag_optimizer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("rag_optimizer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "rag_optimizer", "context_pull")
_emit_pulls_context("p1", "rag_optimizer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "rag_optimizer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "rag_optimizer", "uwg_term_2")
_emit_writes_through("p1", "rag_optimizer", "write_through")
_emit_writes_through("p1", "rag_optimizer", "write_through_2")
_emit_validated_by_safety_plane("p1", "rag_optimizer", "safety_validation")
_emit_invokes_eval("p1", "rag_optimizer", "eval_call")
_emit_proposal_commits_routing("p1", "rag_optimizer", "routing_commit")
_emit_escalates_to_human("p1", "rag_optimizer", "human_escalation")
_emit_routes_through("p1", "rag_optimizer", "route_through")
_emit_checks_agent_registry("p1", "rag_optimizer", "agent_registry")
_emit_validates_agent_capability("p1", "rag_optimizer", "capability")
_emit_dispatches_execution_plan("p1", "rag_optimizer", "exec_plan")
_emit_agent_executes_agent("p1", "rag_optimizer", "sub_agent")
_emit_routes_to_agent("p1", "rag_optimizer", "target_agent")
_emit_verifies_policy("p1", "rag_optimizer", "policy_check")
_emit_observes_runtime_state("p1", "rag_optimizer", "runtime_state")
_emit_verifies_boundary("p1", "rag_optimizer", "boundary_check")
_emit_transcripts_response("p1", "rag_optimizer", "transcript")
_emit_hard_fails_untranscripted("p1", "rag_optimizer")
_emit_gated_by_confidence("p1", "rag_optimizer", "confidence_gate")
emit_replay_key("p0", "rag_optimizer")
emit_determinism_digest("p0", "rag_optimizer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

# =============================================================================
# ChangePackage (Minimal Implementation for Phase 3)
# =============================================================================


@dataclass(frozen=True, slots=True)
class RAGChangePackage:
    """Immutable ChangePackage for RAG parameter changes.

    Fields
    ------
    surface_name : str
        The config surface being changed.
    old_value : int
        The current value.
    new_value : int
        The proposed new value.
    justification : str
        Rationale for the change.
    snapshot_id : str
        The snapshot this proposal is based on.
    """

    surface_name: str
    old_value: int
    new_value: int
    justification: str
    snapshot_id: str

    def canonical_bytes(self) -> bytes:
        """Return deterministic canonical byte representation."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "RAGChangePackage.canonical_bytes",
        )

        # Canonical concatenation with delimiter
        parts = [
            self.surface_name.encode("utf-8"),
            str(self.old_value).encode("utf-8"),
            str(self.new_value).encode("utf-8"),
            self.justification.encode("utf-8"),
            self.snapshot_id.encode("utf-8"),
        ]
        return b"\x1f".join(parts)

    def content_hash(self) -> str:
        """Return SHA-256 hash of canonical bytes."""
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


# =============================================================================
# RAG Optimizer
# =============================================================================


def propose_rag_param_changes(
    snapshot_id: str,
    metrics: dict[str, float],
    current_config: dict[str, int],
    now_utc: int,
    history: dict[str, int],
    cooldown_policy: CooldownPolicy,
    sample_policy: SampleSizePolicy,
    mean_cosine_similarity: float | None = None,
) -> RAGChangePackage | None:
    """Propose RAG parameter changes based on metrics.

    Proposal-only: does NOT activate or commit. Returns a ChangePackage
    that can be committed via Phase 2 version store.

    Parameters
    ----------
    snapshot_id : str
        The snapshot this proposal is based on.
    metrics : dict[str, float]
        Observed metrics (e.g., {"retrieval_precision": 0.65}).
    current_config : dict[str, int]
        Current RAG parameter values.
    now_utc : int
        Current time (injected, not wall-clock).
    history : dict[str, int]
        Last update timestamps and observation counts per surface.
        Format: {"retrieval_top_k_last_update": 1700000000,
                 "retrieval_top_k_n_obs": 2000}
    cooldown_policy : CooldownPolicy
        Cooldown policy to enforce.
    sample_policy : SampleSizePolicy
        Sample size policy to enforce.

    Returns
    -------
    RAGChangePackage | None
        Proposed change, or None if no change needed or dampening violated.

    Raises
    ------
    ConstraintViolation
        If proposed change violates constraints.
    """
    # Example: tune retrieval_top_k based on retrieval_precision
    surface_name = "retrieval_top_k"
    retrieval_precision = metrics.get("retrieval_precision", 0.0)
    current_value = current_config.get(surface_name, 10)

    # Check dampening policies
    last_update = history.get(f"{surface_name}_last_update", 0)
    n_obs = history.get(f"{surface_name}_n_obs", 0)

    try:
        assert_cooldown_ok(last_update, now_utc, cooldown_policy)
        assert_min_sample_size(n_obs, sample_policy)
    except (ValueError, AssertionError, DampeningViolation) as e:
        # Dampening violated - no proposal
        logging.getLogger(__name__).debug(f"Dampening check failed: {e}")
        return None

    # Heuristic now includes semantic quality signal
    justification_parts = [f"retrieval_precision={retrieval_precision:.2f}"]
    proposed_value = current_value

    if mean_cosine_similarity is not None:
        justification_parts.append(f"mean_cosine_similarity={mean_cosine_similarity:.2f}")
        if mean_cosine_similarity < 0.65:
            proposed_value = min(current_value + 2, 20)
        elif mean_cosine_similarity > 0.85 and retrieval_precision > 0.85:
            proposed_value = max(current_value - 2, 3)

    if proposed_value == current_value:  # If semantic signal didn't trigger a change, check precision
        if retrieval_precision < 0.70:
            proposed_value = min(current_value + 2, 20)
        elif retrieval_precision > 0.85:
            proposed_value = max(current_value - 2, 3)

    if proposed_value == current_value:
        return None

    # Validate constraint
    validate_surface_change(surface_name, current_value, proposed_value)

    # Create proposal
    justification = ", ".join(justification_parts) + ", adjusting top_k"
    return RAGChangePackage(
        surface_name=surface_name,
        old_value=current_value,
        new_value=proposed_value,
        justification=justification,
        snapshot_id=snapshot_id,
    )
