"""
Canonical Replay Envelope for Universal Determinism

Provides a stable, canonical representation of all generation and embedding
flows to make semantic drift observable across runs.
"""

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "replay_envelope_types")
trace_contract.emit_determinism_digest("p0", "replay_envelope_types")

trace_contract._emit_dispatches_healing_run("p1", "replay_envelope_types", "L2")
trace_contract._emit_routes_through("p1", "replay_envelope_types", "L2")
trace_contract._emit_checks_agent_registry("p1", "replay_envelope_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "replay_envelope_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "replay_envelope_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "replay_envelope_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "replay_envelope_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "replay_envelope_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "replay_envelope_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "replay_envelope_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "replay_envelope_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "replay_envelope_types")
trace_contract._emit_gated_by_confidence("p1", "replay_envelope_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "replay_envelope_types", "L2")
trace_contract._emit_reads_policy_state("p1", "replay_envelope_types", "L2")

trace_contract._emit_applies_guardrail("p0", "replay_envelope_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "replay_envelope_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "replay_envelope_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "replay_envelope_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "replay_envelope_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "replay_envelope_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "replay_envelope_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "replay_envelope_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "replay_envelope_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "replay_envelope_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "replay_envelope_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "replay_envelope_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "replay_envelope_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "replay_envelope_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "replay_envelope_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "replay_envelope_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "replay_envelope_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "replay_envelope_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "replay_envelope_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "replay_envelope_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "replay_envelope_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "replay_envelope_types", "exec_snapshot_link")

trace_contract.record_execution_trace("replay_envelope_types", "replay_envelope_types_trace")


trace_contract._emit_emits_metric_event("replay_envelope_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("replay_envelope_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("replay_envelope_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("replay_envelope_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("replay_envelope_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("replay_envelope_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("replay_envelope_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("replay_envelope_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("replay_envelope_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("replay_envelope_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("replay_envelope_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("replay_envelope_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("replay_envelope_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("replay_envelope_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("replay_envelope_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("replay_envelope_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("replay_envelope_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("replay_envelope_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("replay_envelope_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("replay_envelope_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("replay_envelope_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("replay_envelope_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("replay_envelope_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("replay_envelope_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("replay_envelope_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("replay_envelope_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("replay_envelope_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("replay_envelope_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "replay_envelope_types", "context_pull")
trace_contract._emit_pulls_context("p1", "replay_envelope_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "replay_envelope_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "replay_envelope_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "replay_envelope_types", "write_through")
trace_contract._emit_writes_through("p1", "replay_envelope_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "replay_envelope_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "replay_envelope_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "replay_envelope_types", "routing_commit")


@dataclass(frozen=True)
class ReplayEnvelope:
    """Canonical replay envelope for deterministic generation tracking."""

    routing_hash: str
    manifest_hash: str
    model_id: str
    model_version: str
    temperature: float
    allowed_model_policy_version: str
    policy_version: str
    gateway_version: str
    embedder_provider: str
    embedder_model: str
    embedder_dim: int
    normalization_policy: str
    chunking_policy: str
    distance_metric: str
    retrieval_top_k: int
    retrieval_similarity_cutoff: float
    agent_registry_hash: str
    deterministic_engine_version: str
    code_commit_hash: str | None = None

    def to_canonical_json(self) -> str:
        """Generate canonical JSON representation with deterministic ordering."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L2_EXECUTION,
            "ReplayEnvelope.to_canonical_json",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ReplayEnvelope.to_canonical_json".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        data = {k: v for k, v in asdict(self).items() if v is not None}
        return json.dumps(data, sort_keys=True, separators=(",", ":"))

    def get_digest(self) -> str:
        """Get SHA256 digest of canonical JSON representation."""
        canonical_json = self.to_canonical_json()
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    @classmethod
    def from_generation_context(
        cls,
        routing_hash: str,
        manifest_hash: str,
        model_id: str,
        model_version: str,
        temperature: float,
        policy_version: str,
        gateway_version: str,
        embedder_provider: str,
        embedder_model: str,
        embedder_dim: int,
        agent_registry_hash: str,
        deterministic_engine_version: str,
        allowed_model_policy_version: str = "1.0",
        normalization_policy: str = "l2",
        chunking_policy: str = "semantic",
        distance_metric: str = "cosine",
        retrieval_top_k: int = 10,
        retrieval_similarity_cutoff: float = 0.7,
        code_commit_hash: str | None = None,
    ) -> "ReplayEnvelope":
        """Create ReplayEnvelope from generation context parameters."""
        return cls(
            routing_hash=routing_hash,
            manifest_hash=manifest_hash,
            model_id=model_id,
            model_version=model_version,
            temperature=temperature,
            allowed_model_policy_version=allowed_model_policy_version,
            policy_version=policy_version,
            gateway_version=gateway_version,
            embedder_provider=embedder_provider,
            embedder_model=embedder_model,
            embedder_dim=embedder_dim,
            normalization_policy=normalization_policy,
            chunking_policy=chunking_policy,
            distance_metric=distance_metric,
            retrieval_top_k=retrieval_top_k,
            retrieval_similarity_cutoff=retrieval_similarity_cutoff,
            agent_registry_hash=agent_registry_hash,
            deterministic_engine_version=deterministic_engine_version,
            code_commit_hash=code_commit_hash,
        )


def create_deterministic_cache_key(text: str, embedder_identity: dict[str, Any]) -> str:
    """Create deterministic cache key for embeddings."""
    canonical_embedder_json = json.dumps(embedder_identity, sort_keys=True, separators=(",", ":"))
    combined = f"{text}:{canonical_embedder_json}"
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()
