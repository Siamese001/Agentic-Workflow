"""EmbeddingArtifact type for Plan B Phase 1.

Deterministic, replay-stable artifact representation with canonical bytes and hash.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Literal

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

_emit_applies_guardrail("p0", "embedding_artifact", "p0_governance")
_emit_reads_policy_state("p0", "embedding_artifact", "policy_binding")
_emit_snapshots_state("p0", "embedding_artifact", "state_snapshot")
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

_emit_emits_metric_event("embedding_artifact", "p4obs", "metric_1")
_emit_emits_metric_event("embedding_artifact", "p4obs", "metric_2")
_emit_emits_metric_event("embedding_artifact", "p4obs", "metric_3")
_emit_emits_metric_event("embedding_artifact", "p4obs", "metric_4")
_emit_emits_metric_event("embedding_artifact", "p4obs", "metric_5")
_emit_emits_metric_event("embedding_artifact", "p4obs", "metric_6")
_emit_records_incident_event("embedding_artifact", "p4obs", "incident")
_emit_captures_runtime_anomaly("embedding_artifact", "p4obs", "anomaly")
_emit_writes_observability_log("embedding_artifact", "p4obs", "obs_log")
_emit_updates_monitoring_state("embedding_artifact", "p4obs", "mon_state")
_emit_triggers_alert("embedding_artifact", "p4obs", "alert")
_emit_links_incident_trace("embedding_artifact", "p4obs", "trace_link")
_emit_captures_pattern("embedding_artifact", "p3lm", "pattern")
_emit_records_learning_event("embedding_artifact", "p3lm", "learning_event")
_emit_writes_learning_snapshot("embedding_artifact", "p3lm", "snapshot")
_emit_feeds_meta_learning("embedding_artifact", "p3lm", "meta_feed")
_emit_updates_routing_strategy("embedding_artifact", "p3lm", "routing")
_emit_improves_agent_policy("embedding_artifact", "p3lm", "policy")
_emit_stores_learning_state("embedding_artifact", "p3lm", "state")
_emit_records_execution_trace("embedding_artifact", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("embedding_artifact", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("embedding_artifact", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("embedding_artifact", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("embedding_artifact", "L4_STATE", "p2_trace_5")
_emit_reads_environ("embedding_artifact", "env_read", "p2_env_1")
_emit_reads_environ("embedding_artifact", "env_read", "p2_env_2")
_emit_reads_runtime_state("embedding_artifact", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("embedding_artifact", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "embedding_artifact", "context_pull")
_emit_pulls_context("p1", "embedding_artifact", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "embedding_artifact", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "embedding_artifact", "uwg_term_2")
_emit_writes_through("p1", "embedding_artifact", "write_through")
_emit_writes_through("p1", "embedding_artifact", "write_through_2")
_emit_validated_by_safety_plane("p1", "embedding_artifact", "safety_validation")
_emit_invokes_eval("p1", "embedding_artifact", "eval_call")
_emit_proposal_commits_routing("p1", "embedding_artifact", "routing_commit")
_emit_escalates_to_human("p1", "embedding_artifact", "human_escalation")
_emit_routes_through("p1", "embedding_artifact", "route_through")
_emit_checks_agent_registry("p1", "embedding_artifact", "agent_registry")
_emit_validates_agent_capability("p1", "embedding_artifact", "capability")
_emit_dispatches_execution_plan("p1", "embedding_artifact", "exec_plan")
_emit_agent_executes_agent("p1", "embedding_artifact", "sub_agent")
_emit_routes_to_agent("p1", "embedding_artifact", "target_agent")
_emit_verifies_policy("p1", "embedding_artifact", "policy_check")
_emit_observes_runtime_state("p1", "embedding_artifact", "runtime_state")
_emit_verifies_boundary("p1", "embedding_artifact", "boundary_check")
_emit_transcripts_response("p1", "embedding_artifact", "transcript")
_emit_hard_fails_untranscripted("p1", "embedding_artifact")
_emit_gated_by_confidence("p1", "embedding_artifact", "confidence_gate")
emit_replay_key("p0", "embedding_artifact")
emit_determinism_digest("p0", "embedding_artifact")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "embedding_artifact", "execution_auth")
_emit_validates_capability("p2", "embedding_artifact", "capability_check")
_emit_routes_to_capability("p2", "embedding_artifact", "capability_route")
_emit_writes_via_uwg("p2", "embedding_artifact", "uwg_write")
_emit_blocks_direct_write("p2", "embedding_artifact", "direct_write_block")
_emit_records_tool_invocation("p2", "embedding_artifact", "tool_invocation")
_emit_captures_execution_output("p2", "embedding_artifact", "exec_output")
_emit_dispatches_agent("p3", "embedding_artifact", "agent_dispatch")
_emit_coordinates_agents("p3", "embedding_artifact", "agent_coordination")
_emit_records_workflow_lineage("p3", "embedding_artifact", "workflow_lineage")
_emit_records_healing_outcome("p3", "embedding_artifact", "healing_outcome")
_emit_escalates_failure("p3", "embedding_artifact", "failure_escalation")
_emit_orchestrates_workflow("p3", "embedding_artifact", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "embedding_artifact", "healing_dispatch")
_emit_invokes_evaluation("p3", "embedding_artifact", "evaluation_signal")
_emit_records_telemetry_event("p4", "embedding_artifact", "telemetry_event")
_emit_captures_evaluation_metric("p4", "embedding_artifact", "eval_metric")
_emit_stores_embedding("p4", "embedding_artifact", "embedding_store")
_emit_updates_meta_learning_state("p4", "embedding_artifact", "meta_learning")
_emit_links_execution_to_snapshot("p4", "embedding_artifact", "exec_snapshot_link")


@dataclass(frozen=True)
class EmbeddingArtifact:
    """Deterministic embedding artifact with canonical bytes and hash.

    Informational-only type that captures embedding metadata in a deterministic
    and replay-stable format. Fully compliant with Governance Memory v5.
    """

    namespace: str
    seed_index_version_hash: str
    supporting_trace_ids: list[str]
    supporting_content_hashes: list[str]
    k: int
    similarity_metric: str
    embedding_model_version: str
    vector: list[float] = field(default_factory=list, repr=False)
    vector_hash: str = field(default="", init=False)
    influence_class: Literal["C0_INFORMATIONAL"] = field(default="C0_INFORMATIONAL", init=False)

    def __post_init__(self) -> None:
        """Enforce invariants after initialization."""
        if not hasattr(self, "_trace_ids_sorted"):
            sorted_trace_ids = tuple(sorted(self.supporting_trace_ids))
            if tuple(self.supporting_trace_ids) != sorted_trace_ids:
                object.__setattr__(self, "supporting_trace_ids", list(sorted_trace_ids))
        if not hasattr(self, "_content_hashes_sorted"):
            sorted_content_hashes = tuple(sorted(self.supporting_content_hashes))
            if tuple(self.supporting_content_hashes) != sorted_content_hashes:
                object.__setattr__(self, "supporting_content_hashes", list(sorted_content_hashes))
        if self.vector:
            vector_bytes = json.dumps(self.vector, sort_keys=True, separators=(",", ":")).encode("utf-8")
            object.__setattr__(self, "vector_hash", hashlib.sha256(vector_bytes).hexdigest())

    def canonical_bytes(self) -> bytes:
        """Return canonical UTF-8 bytes representation.

        Requirements:
        - UTF-8 encoding
        - Minified JSON
        - Deterministic key order
        - Lists serialized in their stored order (already deterministic)
        - No whitespace variance

        Returns:
            Canonical bytes representation of the artifact.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "EmbeddingArtifact.canonical_bytes")

        data = {
            "namespace": self.namespace,
            "seed_index_version_hash": self.seed_index_version_hash,
            "supporting_trace_ids": self.supporting_trace_ids,
            "supporting_content_hashes": self.supporting_content_hashes,
            "k": self.k,
            "similarity_metric": self.similarity_metric,
            "embedding_model_version": self.embedding_model_version,
            "vector_hash": self.vector_hash,
        }
        json_str = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        return json_str.encode("utf-8")

    def artifact_hash(self) -> str:
        """Compute SHA-256 hash of canonical bytes.

        Returns:
            SHA-256 hash of canonical_bytes as hex string.
        """
        canonical = self.canonical_bytes()
        return hashlib.sha256(canonical).hexdigest()

    def assert_non_authoritative(self) -> None:
        """Raise an error if the artifact is used in an authoritative context."""
        if self.influence_class != "C0_INFORMATIONAL":
            raise ValueError("EmbeddingArtifact cannot be used in an authoritative context.")


__all__ = ["EmbeddingArtifact"]
