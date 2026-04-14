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

from .completeness import ContextCompletenessScore, SupportedAnswerCheck

try:
    from agentic_core.runtime.contracts.lifecycle_trace_contract import (
        LayerSegment,
        _emit_records_execution_trace,
    )
except ModuleNotFoundError:

    class LayerSegment:
        L3_ORCHESTRATION = "L3_ORCHESTRATION"

    def _emit_records_execution_trace(*args: Any, **kwargs: Any) -> None:
        return None


def _trace_id(operation: str, payload: str) -> str:
    """Stable trace ID so persistence helpers remain replay-friendly."""
    return hashlib.sha256(f"{operation}|{payload}".encode("utf-8")).hexdigest()[:16]


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
        trace_id = _trace_id(
            "ChunkManifest.canonical_bytes",
            self.chunk_id,
        )
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "ChunkManifest.canonical_bytes",
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
        trace_id = _trace_id(
            "RetrievalEvaluationRecord.canonical_bytes",
            self.query_id,
        )
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "RetrievalEvaluationRecord.canonical_bytes",
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
        trace_id = _trace_id(
            "ChunkManifestRegistry.write",
            manifest.chunk_id,
        )
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "ChunkManifestRegistry.write",
        )

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
        trace_id = _trace_id(
            "ParentChildIndexRegistry.write",
            f"{link.parent_chunk_id}|{link.child_chunk_id}",
        )
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "ParentChildIndexRegistry.write",
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
        trace_id = _trace_id(
            "RetrievalEvaluationRegistry.write",
            record.query_id,
        )
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "RetrievalEvaluationRegistry.write",
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
        trace_id = _trace_id(
            "ContextCompletenessSnapshotStore.write",
            snapshot.snapshot_id,
        )
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "ContextCompletenessSnapshotStore.write",
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
