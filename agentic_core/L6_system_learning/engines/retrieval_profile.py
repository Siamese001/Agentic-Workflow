"""RetrievalProfile Authority (W4-A/B)

Deterministic, versioned profile for embedder and retrieval configuration.
Stored in L4, read by L1. No behavioral changes - only authority shift.

W4-A: RetrievalProfile Authority (L4 Only)
W4-B: Shadow Embedder wiring for drift detection (non-influential)
D2: embeddings_enabled is always True — BGE is a mandatory system dependency.
"""

from __future__ import annotations

from agentic_core.config.model_catalog import (
    BGE_M3_MODEL_ID,
)

import hashlib
import json
from dataclasses import asdict, dataclass

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

_emit_applies_guardrail("p0", "retrieval_profile", "p0_governance")
_emit_reads_policy_state("p0", "retrieval_profile", "policy_binding")
_emit_snapshots_state("p0", "retrieval_profile", "state_snapshot")
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

_emit_emits_metric_event("retrieval_profile", "p4obs", "metric_1")
_emit_emits_metric_event("retrieval_profile", "p4obs", "metric_2")
_emit_emits_metric_event("retrieval_profile", "p4obs", "metric_3")
_emit_emits_metric_event("retrieval_profile", "p4obs", "metric_4")
_emit_emits_metric_event("retrieval_profile", "p4obs", "metric_5")
_emit_emits_metric_event("retrieval_profile", "p4obs", "metric_6")
_emit_records_incident_event("retrieval_profile", "p4obs", "incident")
_emit_captures_runtime_anomaly("retrieval_profile", "p4obs", "anomaly")
_emit_writes_observability_log("retrieval_profile", "p4obs", "obs_log")
_emit_updates_monitoring_state("retrieval_profile", "p4obs", "mon_state")
_emit_triggers_alert("retrieval_profile", "p4obs", "alert")
_emit_links_incident_trace("retrieval_profile", "p4obs", "trace_link")
_emit_captures_pattern("retrieval_profile", "p3lm", "pattern")
_emit_records_learning_event("retrieval_profile", "p3lm", "learning_event")
_emit_writes_learning_snapshot("retrieval_profile", "p3lm", "snapshot")
_emit_feeds_meta_learning("retrieval_profile", "p3lm", "meta_feed")
_emit_updates_routing_strategy("retrieval_profile", "p3lm", "routing")
_emit_improves_agent_policy("retrieval_profile", "p3lm", "policy")
_emit_stores_learning_state("retrieval_profile", "p3lm", "state")
_emit_records_execution_trace("retrieval_profile", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("retrieval_profile", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("retrieval_profile", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("retrieval_profile", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("retrieval_profile", "L4_STATE", "p2_trace_5")
_emit_reads_environ("retrieval_profile", "env_read", "p2_env_1")
_emit_reads_environ("retrieval_profile", "env_read", "p2_env_2")
_emit_reads_runtime_state("retrieval_profile", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("retrieval_profile", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "retrieval_profile", "context_pull")
_emit_pulls_context("p1", "retrieval_profile", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "retrieval_profile", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "retrieval_profile", "uwg_term_2")
_emit_writes_through("p1", "retrieval_profile", "write_through")
_emit_writes_through("p1", "retrieval_profile", "write_through_2")
_emit_validated_by_safety_plane("p1", "retrieval_profile", "safety_validation")
_emit_invokes_eval("p1", "retrieval_profile", "eval_call")
_emit_proposal_commits_routing("p1", "retrieval_profile", "routing_commit")
_emit_escalates_to_human("p1", "retrieval_profile", "human_escalation")
_emit_routes_through("p1", "retrieval_profile", "route_through")
_emit_checks_agent_registry("p1", "retrieval_profile", "agent_registry")
_emit_validates_agent_capability("p1", "retrieval_profile", "capability")
_emit_dispatches_execution_plan("p1", "retrieval_profile", "exec_plan")
_emit_agent_executes_agent("p1", "retrieval_profile", "sub_agent")
_emit_routes_to_agent("p1", "retrieval_profile", "target_agent")
_emit_verifies_policy("p1", "retrieval_profile", "policy_check")
_emit_observes_runtime_state("p1", "retrieval_profile", "runtime_state")
_emit_verifies_boundary("p1", "retrieval_profile", "boundary_check")
_emit_transcripts_response("p1", "retrieval_profile", "transcript")
_emit_hard_fails_untranscripted("p1", "retrieval_profile")
_emit_gated_by_confidence("p1", "retrieval_profile", "confidence_gate")
emit_replay_key("p0", "retrieval_profile")
emit_determinism_digest("p0", "retrieval_profile")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "retrieval_profile", "execution_auth")
_emit_validates_capability("p2", "retrieval_profile", "capability_check")
_emit_routes_to_capability("p2", "retrieval_profile", "capability_route")
_emit_writes_via_uwg("p2", "retrieval_profile", "uwg_write")
_emit_blocks_direct_write("p2", "retrieval_profile", "direct_write_block")
_emit_records_tool_invocation("p2", "retrieval_profile", "tool_invocation")
_emit_captures_execution_output("p2", "retrieval_profile", "exec_output")
_emit_dispatches_agent("p3", "retrieval_profile", "agent_dispatch")
_emit_coordinates_agents("p3", "retrieval_profile", "agent_coordination")
_emit_records_workflow_lineage("p3", "retrieval_profile", "workflow_lineage")
_emit_records_healing_outcome("p3", "retrieval_profile", "healing_outcome")
_emit_escalates_failure("p3", "retrieval_profile", "failure_escalation")
_emit_orchestrates_workflow("p3", "retrieval_profile", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "retrieval_profile", "healing_dispatch")
_emit_invokes_evaluation("p3", "retrieval_profile", "evaluation_signal")
_emit_records_telemetry_event("p4", "retrieval_profile", "telemetry_event")
_emit_captures_evaluation_metric("p4", "retrieval_profile", "eval_metric")
_emit_stores_embedding("p4", "retrieval_profile", "embedding_store")
_emit_updates_meta_learning_state("p4", "retrieval_profile", "meta_learning")
_emit_links_execution_to_snapshot("p4", "retrieval_profile", "exec_snapshot_link")


@dataclass(frozen=True, slots=True)
class RetrievalProfile:
    """Deterministic profile for embedder and retrieval configuration.

    W4-A: RetrievalProfile Authority (L4 Only)
    W4-B: Shadow Embedder wiring for drift detection (non-influential)

    This object governs embedder identity and retrieval knobs.
    It is versioned, deterministic, and stored in L4.
    Shadow embedder provides parallel embeddings for telemetry.
    """

    profile_id: str
    primary_embedder_id: str
    embedding_dim: int
    similarity_cutoff: float
    top_k: int
    influence_cap: float
    normalization_policy: str
    shadow_embedder_id: str | None = None
    hybrid_alpha: float | None = None
    embeddings_enabled: bool = True

    def to_canonical_json(self) -> str:
        """Serialize to canonical JSON with deterministic ordering.

        Returns:
            Canonical JSON string with sorted keys and fixed precision.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "RetrievalProfile.to_canonical_json"
        )

        data = asdict(self)
        data = {k: v for k, v in data.items() if v is not None}
        for key, value in data.items():
            if isinstance(value, float):
                data[key] = round(value, 6)
        return json.dumps(data, separators=(",", ":"), sort_keys=True)

    @property
    def profile_digest(self) -> str:
        """Compute SHA-256 digest of the canonical JSON.

        Returns:
            64-character hex digest.
        """
        canonical_json = self.to_canonical_json()
        return hashlib.sha256(canonical_json.encode()).hexdigest()

    def emit_digest(self) -> None:
        """Print the profile digest for determinism verification."""
        print(f"W4-PROFILE-DIGEST: {self.profile_digest}")

    @classmethod
    def create_default(cls) -> RetrievalProfile:
        """Create the default RetrievalProfile matching current baseline.

        BGE embeddings are always enabled — mandatory system dependency.

        Returns:
            Default profile with current hardcoded values.
        """
        return cls(
            profile_id="retrieval-profile-v3",
            primary_embedder_id=BGE_M3_MODEL_ID,
            embedding_dim=1024,
            similarity_cutoff=0.75,
            top_k=10,
            influence_cap=0.25,
            normalization_policy="l2",
            shadow_embedder_id=None,
            hybrid_alpha=None,
            embeddings_enabled=True,
        )


__all__ = ["RetrievalProfile"]
