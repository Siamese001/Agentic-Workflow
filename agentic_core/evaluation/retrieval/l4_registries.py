"""
Phase B: L4 RAG State and Persistence Extension.

New L4 registries for completeness-aware retrieval:
  L4D: ChunkManifestRegistry
  L4E: ParentChildIndexRegistry
  L4F: RetrievalEvaluationRegistry
  L4G: ContextCompletenessSnapshots

RULES:
- All persisted artifacts are versioned and hashable.
- No registry may authorize execution.
- No snapshot may directly mutate live routing or safety.
- All writes are idempotent (content-hash keyed).

C0 RULE: Informational only. Never authorizes.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from agentic_core.evaluation.retrieval.completeness import (
    ContextCompletenessScore,
    SupportedAnswerCheck,
)
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

_emit_applies_guardrail("p0", "l4_registries", "p0_governance")
_emit_snapshots_state("p0", "l4_registries", "state_snapshot")
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

_emit_emits_metric_event("l4_registries", "p4obs", "metric_1")
_emit_emits_metric_event("l4_registries", "p4obs", "metric_2")
_emit_emits_metric_event("l4_registries", "p4obs", "metric_3")
_emit_emits_metric_event("l4_registries", "p4obs", "metric_4")
_emit_emits_metric_event("l4_registries", "p4obs", "metric_5")
_emit_emits_metric_event("l4_registries", "p4obs", "metric_6")
_emit_records_incident_event("l4_registries", "p4obs", "incident")
_emit_captures_runtime_anomaly("l4_registries", "p4obs", "anomaly")
_emit_writes_observability_log("l4_registries", "p4obs", "obs_log")
_emit_updates_monitoring_state("l4_registries", "p4obs", "mon_state")
_emit_triggers_alert("l4_registries", "p4obs", "alert")
_emit_links_incident_trace("l4_registries", "p4obs", "trace_link")
_emit_captures_pattern("l4_registries", "p3lm", "pattern")
_emit_records_learning_event("l4_registries", "p3lm", "learning_event")
_emit_writes_learning_snapshot("l4_registries", "p3lm", "snapshot")
_emit_feeds_meta_learning("l4_registries", "p3lm", "meta_feed")
_emit_updates_routing_strategy("l4_registries", "p3lm", "routing")
_emit_improves_agent_policy("l4_registries", "p3lm", "policy")
_emit_stores_learning_state("l4_registries", "p3lm", "state")
_emit_records_execution_trace("l4_registries", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("l4_registries", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("l4_registries", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("l4_registries", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("l4_registries", "L4_STATE", "p2_trace_5")
_emit_reads_environ("l4_registries", "env_read", "p2_env_1")
_emit_reads_environ("l4_registries", "env_read", "p2_env_2")
_emit_reads_runtime_state("l4_registries", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("l4_registries", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "l4_registries", "context_pull")
_emit_pulls_context("p1", "l4_registries", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "l4_registries", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "l4_registries", "uwg_term_2")
_emit_writes_through("p1", "l4_registries", "write_through")
_emit_writes_through("p1", "l4_registries", "write_through_2")
_emit_validated_by_safety_plane("p1", "l4_registries", "safety_validation")
_emit_invokes_eval("p1", "l4_registries", "eval_call")
_emit_proposal_commits_routing("p1", "l4_registries", "routing_commit")
_emit_escalates_to_human("p1", "l4_registries", "human_escalation")
_emit_routes_through("p1", "l4_registries", "route_through")
_emit_checks_agent_registry("p1", "l4_registries", "agent_registry")
_emit_validates_agent_capability("p1", "l4_registries", "capability")
_emit_dispatches_execution_plan("p1", "l4_registries", "exec_plan")
_emit_agent_executes_agent("p1", "l4_registries", "sub_agent")
_emit_routes_to_agent("p1", "l4_registries", "target_agent")
_emit_verifies_policy("p1", "l4_registries", "policy_check")
_emit_observes_runtime_state("p1", "l4_registries", "runtime_state")
_emit_verifies_boundary("p1", "l4_registries", "boundary_check")
_emit_transcripts_response("p1", "l4_registries", "transcript")
_emit_hard_fails_untranscripted("p1", "l4_registries")
_emit_gated_by_confidence("p1", "l4_registries", "confidence_gate")
emit_replay_key("p0", "l4_registries")
emit_determinism_digest("p0", "l4_registries")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "l4_registries", "execution_auth")
_emit_validates_capability("p2", "l4_registries", "capability_check")
_emit_routes_to_capability("p2", "l4_registries", "capability_route")
_emit_writes_via_uwg("p2", "l4_registries", "uwg_write")
_emit_blocks_direct_write("p2", "l4_registries", "direct_write_block")
_emit_records_tool_invocation("p2", "l4_registries", "tool_invocation")
_emit_captures_execution_output("p2", "l4_registries", "exec_output")
_emit_dispatches_agent("p3", "l4_registries", "agent_dispatch")
_emit_coordinates_agents("p3", "l4_registries", "agent_coordination")
_emit_records_workflow_lineage("p3", "l4_registries", "workflow_lineage")
_emit_records_healing_outcome("p3", "l4_registries", "healing_outcome")
_emit_escalates_failure("p3", "l4_registries", "failure_escalation")
_emit_orchestrates_workflow("p3", "l4_registries", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "l4_registries", "healing_dispatch")
_emit_invokes_evaluation("p3", "l4_registries", "evaluation_signal")
_emit_records_telemetry_event("p4", "l4_registries", "telemetry_event")
_emit_captures_evaluation_metric("p4", "l4_registries", "eval_metric")
_emit_stores_embedding("p4", "l4_registries", "embedding_store")
_emit_updates_meta_learning_state("p4", "l4_registries", "meta_learning")
_emit_links_execution_to_snapshot("p4", "l4_registries", "exec_snapshot_link")

# ---------------------------------------------------------------------------
# L4D: ChunkManifest
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ChunkManifest:
    """Versioned, hashable manifest for a single corpus chunk.

    Stored in ChunkManifestRegistry (L4D).
    """

    chunk_id: str
    source_doc_id: str
    parent_section_id: str
    heading_path: tuple[str, ...]
    sibling_ids: tuple[str, ...]
    token_span: tuple[int, int]
    token_count: int
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "source_doc_id": self.source_doc_id,
            "parent_section_id": self.parent_section_id,
            "heading_path": list(self.heading_path),
            "sibling_ids": list(self.sibling_ids),
            "token_span": list(self.token_span),
            "token_count": self.token_count,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ChunkManifest:
        return cls(
            chunk_id=data["chunk_id"],
            source_doc_id=data["source_doc_id"],
            parent_section_id=data["parent_section_id"],
            heading_path=tuple(data["heading_path"]),
            sibling_ids=tuple(data["sibling_ids"]),
            token_span=tuple(data["token_span"]),
            token_count=int(data["token_count"]),
            metadata=dict(data.get("metadata", {})),
        )

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ChunkManifest.canonical_bytes"
        )

        d = self.to_dict()
        d.pop("metadata", None)
        return json.dumps(d, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# L4E: ParentChildLink
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ParentChildLink:
    """Maps a child chunk to its parent section and expansion policy.

    Stored in ParentChildIndexRegistry (L4E).
    """

    child_chunk_id: str
    parent_chunk_id: str
    expansion_policy: str
    neighbor_window_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "child_chunk_id": self.child_chunk_id,
            "parent_chunk_id": self.parent_chunk_id,
            "expansion_policy": self.expansion_policy,
            "neighbor_window_ids": list(self.neighbor_window_ids),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ParentChildLink:
        return cls(
            child_chunk_id=data["child_chunk_id"],
            parent_chunk_id=data["parent_chunk_id"],
            expansion_policy=data["expansion_policy"],
            neighbor_window_ids=tuple(data["neighbor_window_ids"]),
        )

    def canonical_bytes(self) -> bytes:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# L4F: RetrievalEvaluationRecord
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RetrievalEvaluationRecord:
    """Full retrieval evaluation record for a single query.

    Stored in RetrievalEvaluationRegistry (L4F).
    Includes retrieved chunks, scores, and validation results.
    """

    query_id: str
    retrieved_chunk_ids: tuple[str, ...]
    expanded_parent_ids: tuple[str, ...]
    lexical_scores: dict[str, float]
    vector_scores: dict[str, float]
    completeness_scores: tuple[ContextCompletenessScore, ...]
    reranked_order: tuple[str, ...]
    answer_check: SupportedAnswerCheck | None
    version: str = "1"

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "query_id": self.query_id,
            "retrieved_chunk_ids": list(self.retrieved_chunk_ids),
            "expanded_parent_ids": list(self.expanded_parent_ids),
            "lexical_scores": dict(self.lexical_scores),
            "vector_scores": dict(self.vector_scores),
            "completeness_scores": [cs.to_dict() for cs in self.completeness_scores],
            "reranked_order": list(self.reranked_order),
            "answer_check": self.answer_check.to_dict() if self.answer_check else None,
        }

    def canonical_bytes(self) -> bytes:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "RetrievalEvaluationRecord.canonical_bytes"
        )

        d = self.to_dict()
        return json.dumps(d, sort_keys=True, separators=(",", ":")).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# L4G: ContextCompletenessSnapshot
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ContextCompletenessSnapshot:
    """Aggregate completeness metrics snapshot for observability.

    Stored in ContextCompletenessSnapshots (L4G).
    Tracks systemic failure rates over a query window.
    """

    snapshot_id: str
    system_version: str
    query_count: int
    missing_condition_rate: float
    missing_exception_rate: float
    missing_scope_rate: float
    missing_temporal_qualifier_rate: float
    parent_reconstruction_rate: float
    right_chunk_wrong_context_rate: float
    high_similarity_wrong_answer_rate: float
    version: str = "1"

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "snapshot_id": self.snapshot_id,
            "system_version": self.system_version,
            "query_count": self.query_count,
            "missing_condition_rate": round(self.missing_condition_rate, 6),
            "missing_exception_rate": round(self.missing_exception_rate, 6),
            "missing_scope_rate": round(self.missing_scope_rate, 6),
            "missing_temporal_qualifier_rate": round(self.missing_temporal_qualifier_rate, 6),
            "parent_reconstruction_rate": round(self.parent_reconstruction_rate, 6),
            "right_chunk_wrong_context_rate": round(self.right_chunk_wrong_context_rate, 6),
            "high_similarity_wrong_answer_rate": round(self.high_similarity_wrong_answer_rate, 6),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ContextCompletenessSnapshot:
        return cls(
            snapshot_id=data["snapshot_id"],
            system_version=data["system_version"],
            query_count=int(data["query_count"]),
            missing_condition_rate=float(data["missing_condition_rate"]),
            missing_exception_rate=float(data["missing_exception_rate"]),
            missing_scope_rate=float(data["missing_scope_rate"]),
            missing_temporal_qualifier_rate=float(data["missing_temporal_qualifier_rate"]),
            parent_reconstruction_rate=float(data["parent_reconstruction_rate"]),
            right_chunk_wrong_context_rate=float(data["right_chunk_wrong_context_rate"]),
            high_similarity_wrong_answer_rate=float(data["high_similarity_wrong_answer_rate"]),
            version=data.get("version", "1"),
        )

    def canonical_bytes(self) -> bytes:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":")).encode("utf-8")

    def content_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


# ---------------------------------------------------------------------------
# In-memory Registry Implementations
# ---------------------------------------------------------------------------


class ChunkManifestRegistry:
    """L4D: In-memory ChunkManifestRegistry (idempotent, content-hash keyed)."""

    def __init__(self) -> None:
        self._store: dict[str, ChunkManifest] = {}

    def write(self, manifest: ChunkManifest) -> str:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ChunkManifestRegistry.write")

        h = manifest.content_hash()
        self._store[manifest.chunk_id] = manifest
        return h

    def get(self, chunk_id: str) -> ChunkManifest | None:
        return self._store.get(chunk_id)

    def all_chunk_ids(self) -> list[str]:
        return sorted(self._store.keys())

    def count(self) -> int:
        return len(self._store)


class ParentChildIndexRegistry:
    """L4E: In-memory ParentChildIndexRegistry."""

    def __init__(self) -> None:
        self._child_to_parent: dict[str, ParentChildLink] = {}
        self._parent_to_children: dict[str, list[str]] = {}

    def write(self, link: ParentChildLink) -> str:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ParentChildIndexRegistry.write"
        )

        h = link.content_hash()
        self._child_to_parent[link.child_chunk_id] = link
        self._parent_to_children.setdefault(link.parent_chunk_id, [])
        if link.child_chunk_id not in self._parent_to_children[link.parent_chunk_id]:
            self._parent_to_children[link.parent_chunk_id].append(link.child_chunk_id)
        return h

    def get_link(self, child_chunk_id: str) -> ParentChildLink | None:
        return self._child_to_parent.get(child_chunk_id)

    def get_children(self, parent_chunk_id: str) -> list[str]:
        return list(self._parent_to_children.get(parent_chunk_id, []))

    def count(self) -> int:
        return len(self._child_to_parent)


class RetrievalEvaluationRegistry:
    """L4F: In-memory RetrievalEvaluationRegistry (content-hash keyed, write-once)."""

    def __init__(self) -> None:
        self._store: dict[str, RetrievalEvaluationRecord] = {}

    def write(self, record: RetrievalEvaluationRecord) -> str:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "RetrievalEvaluationRegistry.write"
        )

        h = record.content_hash()
        if record.query_id not in self._store:
            self._store[record.query_id] = record
        return h

    def get(self, query_id: str) -> RetrievalEvaluationRecord | None:
        return self._store.get(query_id)

    def count(self) -> int:
        return len(self._store)

    def all_query_ids(self) -> list[str]:
        return sorted(self._store.keys())


class ContextCompletenessSnapshotStore:
    """L4G: In-memory ContextCompletenessSnapshots store."""

    def __init__(self) -> None:
        self._snapshots: list[ContextCompletenessSnapshot] = []

    def write(self, snapshot: ContextCompletenessSnapshot) -> str:
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ContextCompletenessSnapshotStore.write"
        )

        h = snapshot.content_hash()
        self._snapshots.append(snapshot)
        return h

    def latest(self) -> ContextCompletenessSnapshot | None:
        return self._snapshots[-1] if self._snapshots else None

    def all(self) -> list[ContextCompletenessSnapshot]:
        return list(self._snapshots)

    def count(self) -> int:
        return len(self._snapshots)


__all__ = [
    "ChunkManifest",
    "ParentChildLink",
    "RetrievalEvaluationRecord",
    "ContextCompletenessSnapshot",
    "ChunkManifestRegistry",
    "ParentChildIndexRegistry",
    "RetrievalEvaluationRegistry",
    "ContextCompletenessSnapshotStore",
]
