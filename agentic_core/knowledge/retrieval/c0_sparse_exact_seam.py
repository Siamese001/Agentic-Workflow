"""W1–W2 generic sparse / lexical retrieval seam for C0-style evidence lanes.

This module is **app-agnostic**: it exposes neutral request/result types and
thin wrappers around the existing hybrid lexical stack
(:class:`~agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine.HybridSearchEngine`
+ :func:`~agentic_core.L4_state.utils.memory.bm25_store.get_sparse_index`).

Downstream apps (e.g. task-specific bindings) supply collection names, lane ids,
and query text via their profiles — **no** domain-specific literals belong here.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Sequence

from agentic_core.L3_orchestration.reasoning.engines.hybrid_search_engine import (
    HybridSearchEngine,
    HybridSearchResult,
)
from agentic_core.runtime.contracts.final_evidence_contract import (
    ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
    EvidenceItem,
    STATUS_UNKNOWN,
)


class SparseLexicalLaneStatus(str, Enum):
    """Lane outcome — intentionally **not** a PASS/FAIL verdict."""

    OK = "OK"
    EMPTY = "EMPTY"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True, slots=True)
class SparseLexicalQuerySpec:
    """Neutral sparse/lexical query request."""

    lane_id: str
    query_text: str
    top_k: int = 10
    #: Name passed to ``get_sparse_index`` (canonical sidecar collections only).
    sparse_index_collection_name: str = ""
    #: Optional metadata equality filter applied to lexical hits (deterministic).
    metadata_filter: Mapping[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class SparseLexicalHit:
    """Single lexical / sparse hit in a transport-neutral shape."""

    chunk_id: str
    source_id: str
    text: str
    span_ref: str
    lexical_score: float
    dense_score: float
    metadata: Mapping[str, Any]
    citation_ref: str


@dataclass(frozen=True, slots=True)
class SparseLexicalLaneOutcome:
    """Sparse lane execution outcome (evidence-only; no L4 writes)."""

    lane_id: str
    status: SparseLexicalLaneStatus
    hits: tuple[SparseLexicalHit, ...]
    receipt_ref: str
    #: Raw engine rows for merge helpers (stable copy).
    hybrid_rows: tuple[HybridSearchResult, ...]


def _metadata_matches(row_meta: Mapping[str, Any], flt: Mapping[str, Any] | None) -> bool:
    if not flt:
        return True
    for key, expected in flt.items():
        if key not in row_meta or row_meta[key] != expected:
            return False
    return True


def _hybrid_row_to_hit(row: HybridSearchResult) -> SparseLexicalHit:
    meta = dict(row.metadata) if row.metadata else {}
    source_id = str(meta.get("source_document_id") or meta.get("source_id") or row.chunk_id)
    span = row.content[:120] if row.content else ""
    cite = f"urn:chunk:{row.chunk_id}"
    return SparseLexicalHit(
        chunk_id=row.chunk_id,
        source_id=source_id,
        text=row.content,
        span_ref=span,
        lexical_score=float(row.lexical_score),
        dense_score=float(row.vector_score),
        metadata=meta,
        citation_ref=cite,
    )


def format_sparse_lane_receipt(
    lane_id: str,
    status: SparseLexicalLaneStatus,
    hit_count: int,
) -> str:
    """Single opaque receipt token suitable for ``FinalEvidenceContract.sparse_search_refs``."""
    safe_lane = lane_id.replace(":", "_")
    return f"ref:sparse:lane:{safe_lane}:status={status.value}:hits={hit_count}"


def query_sparse_lexical_lane(spec: SparseLexicalQuerySpec) -> SparseLexicalLaneOutcome:
    """Execute lexical retrieval via the hybrid engine (FTS5 sidecar when available).

    * ``UNAVAILABLE`` — empty collection name, unknown collection, missing sidecar,
      or import/runtime failure on the sparse path (soft-fail).
    * ``EMPTY`` — lane reachable but zero hits after filtering / query.
    * ``OK`` — one or more hits.
    """
    name = (spec.sparse_index_collection_name or "").strip()
    if not name:
        r = format_sparse_lane_receipt(spec.lane_id, SparseLexicalLaneStatus.UNAVAILABLE, 0)
        return SparseLexicalLaneOutcome(
            lane_id=spec.lane_id,
            status=SparseLexicalLaneStatus.UNAVAILABLE,
            hits=(),
            receipt_ref=r,
            hybrid_rows=(),
        )

    engine = HybridSearchEngine(chroma_client=None, top_k=max(1, int(spec.top_k)))
    rows = engine._lexical_search(  # noqa: SLF001 — intentional reuse of hardened backend
        spec.query_text,
        name,
        governance_filter=None,
    )

    if not rows:
        # Distinguish missing index vs empty query: engine returns [] for both;
        # probe availability without mutating caller state.
        try:
            from agentic_core.L4_state.utils.memory.bm25_store import get_sparse_index
        except ImportError:
            idx = None
        else:
            try:
                idx = get_sparse_index(name)
            except (OSError, RuntimeError, ValueError, TypeError):
                idx = None
        if idx is None or not getattr(idx, "is_available", False):
            st = SparseLexicalLaneStatus.UNAVAILABLE
        else:
            st = SparseLexicalLaneStatus.EMPTY
        r = format_sparse_lane_receipt(spec.lane_id, st, 0)
        return SparseLexicalLaneOutcome(
            lane_id=spec.lane_id,
            status=st,
            hits=(),
            receipt_ref=r,
            hybrid_rows=(),
        )

    filtered: list[HybridSearchResult] = [
        row for row in rows if _metadata_matches(row.metadata or {}, spec.metadata_filter)
    ]
    if not filtered:
        r = format_sparse_lane_receipt(spec.lane_id, SparseLexicalLaneStatus.EMPTY, 0)
        return SparseLexicalLaneOutcome(
            lane_id=spec.lane_id,
            status=SparseLexicalLaneStatus.EMPTY,
            hits=(),
            receipt_ref=r,
            hybrid_rows=(),
        )

    hits = tuple(_hybrid_row_to_hit(row) for row in filtered)
    r = format_sparse_lane_receipt(spec.lane_id, SparseLexicalLaneStatus.OK, len(hits))
    return SparseLexicalLaneOutcome(
        lane_id=spec.lane_id,
        status=SparseLexicalLaneStatus.OK,
        hits=hits,
        receipt_ref=r,
        hybrid_rows=tuple(filtered),
    )


def stabilize_hybrid_order(results: Sequence[HybridSearchResult]) -> list[HybridSearchResult]:
    """Deterministic ordering: score desc, ``chunk_id`` asc tie-break."""
    return sorted(results, key=lambda r: (-r.combined_score, r.chunk_id))


def dedupe_hybrid_by_chunk_id(results: Sequence[HybridSearchResult]) -> tuple[HybridSearchResult, ...]:
    """Deduplicate by ``chunk_id``, keeping the row with maximum ``combined_score``."""
    ordered = stabilize_hybrid_order(results)
    deduped = HybridSearchEngine._deduplicate_results(ordered)  # noqa: SLF001 — reuse canonical dedupe
    return tuple(stabilize_hybrid_order(deduped))


def merge_dense_sparse_rrf(
    dense: Sequence[HybridSearchResult],
    sparse: Sequence[HybridSearchResult],
    *,
    rrf_k: int | None = None,
) -> tuple[HybridSearchResult, ...]:
    """Fuse dense + sparse lists with reciprocal rank fusion (canonical ``_rrf_fuse``)."""
    fused = HybridSearchEngine._rrf_fuse(list(dense), list(sparse), k=rrf_k)  # noqa: SLF001
    return tuple(stabilize_hybrid_order(fused))


def evidence_items_from_merged_hybrid(
    merged: Sequence[HybridSearchResult],
    *,
    lane_id: str,
    query_vec_ref: str,
    retrieval_run_ref: str,
) -> tuple[EvidenceItem, ...]:
    """Map fused hybrid rows onto :class:`EvidenceItem` (AG-4) without schema changes.

    Per-item ``support_status`` remains ``UNKNOWN`` — this helper does **not**
    assert sufficiency or PASS for C0.
    """
    items: list[EvidenceItem] = []
    for row in merged:
        methods: list[str] = []
        if row.vector_score > 0.0:
            methods.append("dense")
        if row.lexical_score > 0.0:
            methods.append("sparse")
        if not methods:
            methods.append("metadata")
        retrieval_method = ",".join(methods)
        digest_src = f"{row.chunk_id}|{row.content}|{row.vector_score}|{row.lexical_score}"
        digest = hashlib.sha256(digest_src.encode("utf-8")).hexdigest()[:32]
        meta_json = json.dumps(row.metadata, sort_keys=True) if row.metadata else ""
        items.append(
            EvidenceItem(
                source=f"retrieval:{lane_id}:{row.chunk_id}",
                content=row.content,
                source_type="retrieved_chunk",
                source_id=str(row.metadata.get("source_document_id") or row.chunk_id),
                citation_anchor=f"urn:chunk:{row.chunk_id}",
                chunk_digest=digest[-32:],
                dense_score=float(row.vector_score),
                bm25_score=float(row.lexical_score),
                fact_vec_ref=query_vec_ref if row.vector_score > 0.0 else "",
                query_vec_ref=query_vec_ref if row.vector_score > 0.0 else "",
                retrieval_method=retrieval_method,
                retrieval_run_ref=retrieval_run_ref,
                allowed_prompt_slot=ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
                support_status=STATUS_UNKNOWN,
                stratum="CANONICAL",
                source_uri_or_ref=meta_json[:512],
            ),
        )
    return tuple(items)


def fec_sparse_refs_from_lane_outcomes(*receipts: str) -> tuple[str, ...]:
    """Bundle lane receipts for ``FinalEvidenceContract.sparse_search_refs``."""
    return tuple(receipts)


def filter_candidates_exact_subphrase(
    candidates: Sequence[tuple[str, str, Mapping[str, Any]]],
    phrase: str,
) -> tuple[tuple[str, str, Mapping[str, Any]], ...]:
    """Pure exact-subphrase filter over neutral (id, text, metadata) rows.

    Used for deterministic unit tests **without** claiming BM25/FTS behaviour.
    """
    needle = phrase.strip()
    if not needle:
        return ()
    out: list[tuple[str, str, Mapping[str, Any]]] = []
    for doc_id, text, meta in candidates:
        if needle in text:
            out.append((doc_id, text, meta))
    return tuple(out)
