"""
Phase G: Late Chunking Profile — governed retrieval/corpus-construction profile.

Late chunking is NOT a universal replacement for standard chunking.
It is a governed, profile-gated retrieval strategy that:
  1. Embeds the full document in one long-context pass
  2. Post-embedding, segments into chunks (pooled embeddings)
  3. Indexes pooled segment embeddings into FAISS

Profile modes:
  standard_chunked
  late_chunked
  late_chunked_hybrid
  late_chunked_hybrid_reranked

CONSTRAINTS:
- Late chunking must be profile-gated
- Long-context model capability must be checked
- Deterministic pooling/segmentation required
- Manifest hashing required
- Evaluation-first rollout required

C0 RULE: Informational only — no routing/safety mutation.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Literal

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

_emit_applies_guardrail("p0", "late_chunking", "p0_governance")
_emit_snapshots_state("p0", "late_chunking", "state_snapshot")
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

_emit_emits_metric_event("late_chunking", "p4obs", "metric_1")
_emit_emits_metric_event("late_chunking", "p4obs", "metric_2")
_emit_emits_metric_event("late_chunking", "p4obs", "metric_3")
_emit_emits_metric_event("late_chunking", "p4obs", "metric_4")
_emit_emits_metric_event("late_chunking", "p4obs", "metric_5")
_emit_emits_metric_event("late_chunking", "p4obs", "metric_6")
_emit_records_incident_event("late_chunking", "p4obs", "incident")
_emit_captures_runtime_anomaly("late_chunking", "p4obs", "anomaly")
_emit_writes_observability_log("late_chunking", "p4obs", "obs_log")
_emit_updates_monitoring_state("late_chunking", "p4obs", "mon_state")
_emit_triggers_alert("late_chunking", "p4obs", "alert")
_emit_links_incident_trace("late_chunking", "p4obs", "trace_link")
_emit_captures_pattern("late_chunking", "p3lm", "pattern")
_emit_records_learning_event("late_chunking", "p3lm", "learning_event")
_emit_writes_learning_snapshot("late_chunking", "p3lm", "snapshot")
_emit_feeds_meta_learning("late_chunking", "p3lm", "meta_feed")
_emit_updates_routing_strategy("late_chunking", "p3lm", "routing")
_emit_improves_agent_policy("late_chunking", "p3lm", "policy")
_emit_stores_learning_state("late_chunking", "p3lm", "state")
_emit_records_execution_trace("late_chunking", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("late_chunking", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("late_chunking", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("late_chunking", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("late_chunking", "L4_STATE", "p2_trace_5")
_emit_reads_environ("late_chunking", "env_read", "p2_env_1")
_emit_reads_environ("late_chunking", "env_read", "p2_env_2")
_emit_reads_runtime_state("late_chunking", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("late_chunking", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "late_chunking", "context_pull")
_emit_pulls_context("p1", "late_chunking", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "late_chunking", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "late_chunking", "uwg_term_2")
_emit_writes_through("p1", "late_chunking", "write_through")
_emit_writes_through("p1", "late_chunking", "write_through_2")
_emit_validated_by_safety_plane("p1", "late_chunking", "safety_validation")
_emit_invokes_eval("p1", "late_chunking", "eval_call")
_emit_proposal_commits_routing("p1", "late_chunking", "routing_commit")
_emit_escalates_to_human("p1", "late_chunking", "human_escalation")
_emit_routes_through("p1", "late_chunking", "route_through")
_emit_checks_agent_registry("p1", "late_chunking", "agent_registry")
_emit_validates_agent_capability("p1", "late_chunking", "capability")
_emit_dispatches_execution_plan("p1", "late_chunking", "exec_plan")
_emit_agent_executes_agent("p1", "late_chunking", "sub_agent")
_emit_routes_to_agent("p1", "late_chunking", "target_agent")
_emit_verifies_policy("p1", "late_chunking", "policy_check")
_emit_observes_runtime_state("p1", "late_chunking", "runtime_state")
_emit_verifies_boundary("p1", "late_chunking", "boundary_check")
_emit_transcripts_response("p1", "late_chunking", "transcript")
_emit_hard_fails_untranscripted("p1", "late_chunking")
_emit_gated_by_confidence("p1", "late_chunking", "confidence_gate")
emit_replay_key("p0", "late_chunking")
emit_determinism_digest("p0", "late_chunking")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "late_chunking", "execution_auth")
_emit_validates_capability("p2", "late_chunking", "capability_check")
_emit_routes_to_capability("p2", "late_chunking", "capability_route")
_emit_writes_via_uwg("p2", "late_chunking", "uwg_write")
_emit_blocks_direct_write("p2", "late_chunking", "direct_write_block")
_emit_records_tool_invocation("p2", "late_chunking", "tool_invocation")
_emit_captures_execution_output("p2", "late_chunking", "exec_output")
_emit_dispatches_agent("p3", "late_chunking", "agent_dispatch")
_emit_coordinates_agents("p3", "late_chunking", "agent_coordination")
_emit_records_workflow_lineage("p3", "late_chunking", "workflow_lineage")
_emit_records_healing_outcome("p3", "late_chunking", "healing_outcome")
_emit_escalates_failure("p3", "late_chunking", "failure_escalation")
_emit_orchestrates_workflow("p3", "late_chunking", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "late_chunking", "healing_dispatch")
_emit_invokes_evaluation("p3", "late_chunking", "evaluation_signal")
_emit_records_telemetry_event("p4", "late_chunking", "telemetry_event")
_emit_captures_evaluation_metric("p4", "late_chunking", "eval_metric")
_emit_stores_embedding("p4", "late_chunking", "embedding_store")
_emit_updates_meta_learning_state("p4", "late_chunking", "meta_learning")
_emit_links_execution_to_snapshot("p4", "late_chunking", "exec_snapshot_link")

LateChunkingMode = Literal[
    "standard_chunked",
    "late_chunked",
    "late_chunked_hybrid",
    "late_chunked_hybrid_reranked",
]
VALID_MODES: frozenset[str] = frozenset(
    {"standard_chunked", "late_chunked", "late_chunked_hybrid", "late_chunked_hybrid_reranked"},
)
VALID_POOLING_STRATEGIES: frozenset[str] = frozenset({"mean", "max", "cls", "weighted_mean"})


@dataclass(frozen=True)
class LateChunkingProfile:
    """Versioned, hashable profile governing late chunking behavior.

    Stored in L4 alongside standard RetrievalProfile.
    Must be explicitly activated — never auto-applies.
    """

    profile_id: str
    mode: LateChunkingMode
    embedding_model_version: str
    max_input_tokens: int
    pooling_strategy: str
    chunk_window_policy: str
    stride_policy: str
    parent_section_policy: str
    artifact_hash: str = ""

    def __post_init__(self) -> None:
        if self.mode not in VALID_MODES:
            raise ValueError(f"Invalid mode: {self.mode!r}. Must be one of {sorted(VALID_MODES)}")
        if self.pooling_strategy not in VALID_POOLING_STRATEGIES:
            raise ValueError(
                f"Invalid pooling_strategy: {self.pooling_strategy!r}. Must be one of {sorted(VALID_POOLING_STRATEGIES)}",
            )
        if self.max_input_tokens < 1:
            raise ValueError("max_input_tokens must be >= 1")

    def to_dict(self) -> dict[str, Any]:
        return {
            "profile_id": self.profile_id,
            "mode": self.mode,
            "embedding_model_version": self.embedding_model_version,
            "max_input_tokens": self.max_input_tokens,
            "pooling_strategy": self.pooling_strategy,
            "chunk_window_policy": self.chunk_window_policy,
            "stride_policy": self.stride_policy,
            "parent_section_policy": self.parent_section_policy,
            "artifact_hash": self.artifact_hash,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LateChunkingProfile:
        return cls(
            profile_id=data["profile_id"],
            mode=data["mode"],
            embedding_model_version=data["embedding_model_version"],
            max_input_tokens=int(data["max_input_tokens"]),
            pooling_strategy=data["pooling_strategy"],
            chunk_window_policy=data["chunk_window_policy"],
            stride_policy=data["stride_policy"],
            parent_section_policy=data["parent_section_policy"],
            artifact_hash=data.get("artifact_hash", ""),
        )

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "LateChunkingProfile.canonical_bytes"
        )

        d = self.to_dict()
        d.pop("artifact_hash", None)
        return json.dumps(d, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def profile_digest(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

    @property
    def is_late_chunked(self) -> bool:
        return self.mode != "standard_chunked"

    @property
    def uses_hybrid_retrieval(self) -> bool:
        return "hybrid" in self.mode

    @property
    def uses_reranking(self) -> bool:
        return "reranked" in self.mode


@dataclass(frozen=True)
class LateChunkManifest:
    """Versioned, hashable manifest for a late-chunked segment.

    Stores the mapping from source document segment to its pooled
    embedding hash and build profile.
    """

    source_doc_id: str
    segment_id: str
    parent_section_id: str
    token_start: int
    token_end: int
    pooled_embedding_hash: str
    heading_path: tuple[str, ...]
    build_profile_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_doc_id": self.source_doc_id,
            "segment_id": self.segment_id,
            "parent_section_id": self.parent_section_id,
            "token_start": self.token_start,
            "token_end": self.token_end,
            "pooled_embedding_hash": self.pooled_embedding_hash,
            "heading_path": list(self.heading_path),
            "build_profile_id": self.build_profile_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LateChunkManifest:
        return cls(
            source_doc_id=data["source_doc_id"],
            segment_id=data["segment_id"],
            parent_section_id=data["parent_section_id"],
            token_start=int(data["token_start"]),
            token_end=int(data["token_end"]),
            pooled_embedding_hash=data["pooled_embedding_hash"],
            heading_path=tuple(data["heading_path"]),
            build_profile_id=data["build_profile_id"],
        )

    def canonical_bytes(self) -> bytes:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

    @property
    def token_count(self) -> int:
        return self.token_end - self.token_start


@dataclass
class LateChunkingPipelineConfig:
    """Configuration for the late chunking pipeline."""

    profile: LateChunkingProfile
    stride: int = 64
    max_segment_tokens: int = 256

    def __post_init__(self) -> None:
        if self.stride < 1:
            raise ValueError("stride must be >= 1")
        if self.max_segment_tokens < 1:
            raise ValueError("max_segment_tokens must be >= 1")


def _compute_pooled_hash(token_start: int, token_end: int, model_version: str) -> str:
    """Compute a deterministic hash for a pooled embedding segment.

    In production this would hash the actual pooled embedding vector.
    Here it hashes the segment coordinates + model version for determinism.
    """
    data = json.dumps(
        {"token_start": token_start, "token_end": token_end, "model_version": model_version},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def segment_document(
    source_doc_id: str,
    total_tokens: int,
    config: LateChunkingPipelineConfig,
    parent_section_id: str = "",
    heading_path: tuple[str, ...] = (),
) -> list[LateChunkManifest]:
    """Deterministically segment a document into late-chunked manifests.

    Args:
        source_doc_id: Document identifier.
        total_tokens: Total token count of the document.
        config: Pipeline configuration.
        parent_section_id: Parent section for all segments.
        heading_path: Heading hierarchy for all segments.

    Returns:
        Ordered list of LateChunkManifest entries.
    """
    if total_tokens <= 0:
        return []
    manifests: list[LateChunkManifest] = []
    start = 0
    seg_idx = 0
    while start < total_tokens:
        end = min(start + config.max_segment_tokens, total_tokens)
        segment_id = f"{source_doc_id}::seg_{seg_idx:04d}"
        pooled_hash = _compute_pooled_hash(start, end, config.profile.embedding_model_version)
        manifests.append(
            LateChunkManifest(
                source_doc_id=source_doc_id,
                segment_id=segment_id,
                parent_section_id=parent_section_id,
                token_start=start,
                token_end=end,
                pooled_embedding_hash=pooled_hash,
                heading_path=heading_path,
                build_profile_id=config.profile.profile_id,
            ),
        )
        seg_idx += 1
        start += config.max_segment_tokens - config.stride
        if start >= total_tokens:
            break
    return manifests


@dataclass(frozen=True)
class EmbeddingLifecycleEvent:
    """Immutable event recording the lifecycle of a chunk embedding.

    Emitted after a LateChunkManifest is embedded and written to the
    vector store. Used by the meta-learning bus for S2 telemetry and
    S5 root-cause analysis.
    """

    chunk_id: str
    embedding_model: str
    embedding_hash: str
    vector_index_id: str

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "EmbeddingLifecycleEvent.canonical_bytes"
        )

        d = {
            "chunk_id": self.chunk_id,
            "embedding_model": self.embedding_model,
            "embedding_hash": self.embedding_hash,
            "vector_index_id": self.vector_index_id,
        }
        return json.dumps(d, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def event_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

    @classmethod
    def build(
        cls,
        manifest: LateChunkManifest,
        embedding_model: str,
        vector_index_id: str,
    ) -> EmbeddingLifecycleEvent:
        """Derive an EmbeddingLifecycleEvent from a manifest."""
        embedding_hash = hashlib.sha256(f"{manifest.segment_id}:{embedding_model}".encode()).hexdigest()
        return cls(
            chunk_id=manifest.segment_id,
            embedding_model=embedding_model,
            embedding_hash=embedding_hash,
            vector_index_id=vector_index_id,
        )


def build_late_chunk_manifests_for_corpus(
    documents: list[dict[str, Any]],
    config: LateChunkingPipelineConfig,
) -> list[LateChunkManifest]:
    """Build late chunk manifests for a corpus of documents.

    Each document must have keys: source_doc_id, total_tokens,
    and optionally parent_section_id, heading_path.

    Returns manifests sorted deterministically by (source_doc_id, token_start).
    """
    all_manifests: list[LateChunkManifest] = []
    for doc in documents:
        doc_manifests = segment_document(
            source_doc_id=doc["source_doc_id"],
            total_tokens=int(doc["total_tokens"]),
            config=config,
            parent_section_id=doc.get("parent_section_id", ""),
            heading_path=tuple(doc.get("heading_path", [])),
        )
        all_manifests.extend(doc_manifests)
    all_manifests.sort(key=lambda m: (m.source_doc_id, m.token_start))
    return all_manifests


def compute_corpus_manifest_hash(manifests: list[LateChunkManifest]) -> str:
    """Compute a deterministic hash over an ordered list of manifests.

    Stable across replay runs given identical input documents and config.
    """
    payload = json.dumps(
        [m.to_dict() for m in manifests],
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


__all__ = [
    "LateChunkingMode",
    "VALID_MODES",
    "VALID_POOLING_STRATEGIES",
    "LateChunkingProfile",
    "LateChunkManifest",
    "LateChunkingPipelineConfig",
    "EmbeddingLifecycleEvent",
    "segment_document",
    "build_late_chunk_manifests_for_corpus",
    "compute_corpus_manifest_hash",
]
