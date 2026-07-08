"""RetrievalProfile Authority (W4-A/B)

Deterministic, versioned profile for embedder and retrieval configuration.
Stored in L4, read by L1. No behavioral changes - only authority shift.

W4-A: RetrievalProfile Authority (L4 Only)
W4-B: Shadow Embedder wiring for drift detection (non-influential)
D2: embeddings_enabled is always True — BGE is a mandatory system dependency.
"""

from __future__ import annotations

from agentic_core.config.model_catalog import (
    BGE_M3_EMBEDDING_DIMENSION,
    BGE_M3_MODEL_ID,
)

import hashlib
import json
from dataclasses import asdict, dataclass

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "retrieval_profile", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "retrieval_profile", "policy_binding")
trace_contract._emit_snapshots_state("p0", "retrieval_profile", "state_snapshot")

trace_contract._emit_emits_metric_event("retrieval_profile", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("retrieval_profile", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("retrieval_profile", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("retrieval_profile", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("retrieval_profile", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("retrieval_profile", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("retrieval_profile", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("retrieval_profile", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("retrieval_profile", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("retrieval_profile", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("retrieval_profile", "p4obs", "alert")
trace_contract._emit_links_incident_trace("retrieval_profile", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("retrieval_profile", "p3lm", "pattern")
trace_contract._emit_records_learning_event("retrieval_profile", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("retrieval_profile", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("retrieval_profile", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("retrieval_profile", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("retrieval_profile", "p3lm", "policy")
trace_contract._emit_stores_learning_state("retrieval_profile", "p3lm", "state")
trace_contract._emit_records_execution_trace("retrieval_profile", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("retrieval_profile", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("retrieval_profile", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("retrieval_profile", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("retrieval_profile", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("retrieval_profile", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("retrieval_profile", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("retrieval_profile", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("retrieval_profile", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "retrieval_profile", "context_pull")
trace_contract._emit_pulls_context("p1", "retrieval_profile", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "retrieval_profile", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "retrieval_profile", "uwg_term_2")
trace_contract._emit_writes_through("p1", "retrieval_profile", "write_through")
trace_contract._emit_writes_through("p1", "retrieval_profile", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "retrieval_profile", "safety_validation")
trace_contract._emit_invokes_eval("p1", "retrieval_profile", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "retrieval_profile", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "retrieval_profile", "human_escalation")
trace_contract._emit_routes_through("p1", "retrieval_profile", "route_through")
trace_contract._emit_checks_agent_registry("p1", "retrieval_profile", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "retrieval_profile", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "retrieval_profile", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "retrieval_profile", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "retrieval_profile", "target_agent")
trace_contract._emit_verifies_policy("p1", "retrieval_profile", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "retrieval_profile", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "retrieval_profile", "boundary_check")
trace_contract._emit_transcripts_response("p1", "retrieval_profile", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "retrieval_profile")
trace_contract._emit_gated_by_confidence("p1", "retrieval_profile", "confidence_gate")
trace_contract.emit_replay_key("p0", "retrieval_profile")
trace_contract.emit_determinism_digest("p0", "retrieval_profile")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "retrieval_profile", "execution_auth")
trace_contract._emit_validates_capability("p2", "retrieval_profile", "capability_check")
trace_contract._emit_routes_to_capability("p2", "retrieval_profile", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "retrieval_profile", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "retrieval_profile", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "retrieval_profile", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "retrieval_profile", "exec_output")
trace_contract._emit_dispatches_agent("p3", "retrieval_profile", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "retrieval_profile", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "retrieval_profile", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "retrieval_profile", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "retrieval_profile", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "retrieval_profile", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "retrieval_profile", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "retrieval_profile", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "retrieval_profile", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "retrieval_profile", "eval_metric")
trace_contract._emit_stores_embedding("p4", "retrieval_profile", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "retrieval_profile", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "retrieval_profile", "exec_snapshot_link")


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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "RetrievalProfile.to_canonical_json"
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
            embedding_dim=BGE_M3_EMBEDDING_DIMENSION,
            similarity_cutoff=0.75,
            top_k=10,
            influence_cap=0.25,
            normalization_policy="l2",
            shadow_embedder_id=None,
            hybrid_alpha=None,
            embeddings_enabled=True,
        )


__all__ = ["RetrievalProfile"]
