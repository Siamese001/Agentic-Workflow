"""Hybrid Recall Stage.

Dense and sparse retrieval with merge/dedup candidate list.

Architecture reference:
  - 00D_sparse_index_hybrid_merge.md §Hybrid Merge (sparse wins on IDs)
  - C5_Retrieval_Prompt_Assembly.md §C0 Context Engine / Evidence Fetch
  - 03_Route_Decision_Switching.md §Pre-Routing Gates

Changes from initial version:
  - SparseIndex / Bm25Store wired in (real sparse rail from L4_state)
  - RetrievalPlan accepted; replay_key / policy_hash stamped on every result
  - Sparse-wins-on-IDs merge rule per 00D architecture
  - Injectable vector_store protocol for real dense recall (safe no-op if absent)
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from tqdm import tqdm

from agentic_core.knowledge.retrieval.retrieval_plan import RetrievalMode
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_records_telemetry_event,
)

log = logging.getLogger(__name__)


@dataclass
class RecallResult:
    """Result from recall stage.

    Attributes
    ----------
    doc_id : str
        Canonical chunk / document identifier.
    score : float
        Final merged score (dense * vector_weight + sparse * sparse_weight).
    source : str
        ``"dense"``, ``"sparse"``, or ``"both"``.
    content : str
        Raw text payload.
    metadata : dict
        Includes ``dense_score``, ``sparse_score``, ``replay_key``,
        ``policy_hash``, ``plan_id``, and any store-specific fields.
    """

    doc_id: str
    score: float
    source: str  # "dense", "sparse", "both"
    content: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# VectorStore protocol (injectable dense backend)
# ---------------------------------------------------------------------------


@runtime_checkable
class VectorStore(Protocol):
    """Minimal interface for an injectable dense vector backend."""

    def query(
        self,
        query_vector: list[float],
        top_k: int,
        scope_filter: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        """Return top-k hits as dicts with keys: id, content, score, metadata."""
        pass  # pragma: no cover


# ---------------------------------------------------------------------------
# HybridRecallStage
# ---------------------------------------------------------------------------


class HybridRecallStage:
    """Hybrid retrieval: dense + sparse with governance metadata propagation.

    Implements Evidence Fetch (C0 Context Engine) per C5 §Evidence Fetch:
      1. Dense path  — real VectorStore when injected; safe no-op otherwise.
      2. Sparse path — real SparseIndex (FTS5) and/or Bm25Store (in-memory).
      3. Hybrid merge — sparse wins on IDs per 00D §Hybrid Merge rule.
      4. replay_key / policy_hash stamped on every RecallResult.metadata.

    Args:
        vector_weight: Weight applied to dense scores (0–1).
        sparse_weight: Weight applied to sparse scores (0–1).
        top_k: Default maximum results; overridden by plan.top_k when present.
        vector_store: Injectable dense backend (``VectorStore`` protocol).
            ``None`` → dense path returns nothing (safe degradation).
        sparse_store: Injectable in-memory ``Bm25Store`` instance.
            ``None`` → Bm25Store path skipped.
        sparse_fts_collection: Collection name for the FTS5 ``SparseIndex``.
            ``None`` → FTS5 path skipped.
    """

    def __init__(
        self,
        vector_weight: float = 0.5,
        sparse_weight: float = 0.5,
        top_k: int = 20,
        vector_store: VectorStore | None = None,
        sparse_store: Any | None = None,
        sparse_fts_collection: str | None = None,
        graph_stage: Any | None = None,
    ) -> None:
        self.vector_weight = vector_weight
        self.sparse_weight = sparse_weight
        self.top_k = top_k

        self._vector_store: VectorStore | None = vector_store
        self._sparse_store = sparse_store
        self._sparse_fts_collection = sparse_fts_collection
        self._sparse_fts_index: Any | None = None  # lazily resolved
        self._graph_stage = graph_stage  # GraphRecallStage or None (C0.3)

        log.info(
            "HybridRecallStage initialized (vector=%.2f, sparse=%.2f, "
            "dense_wired=%s, sparse_store=%s, fts=%s, graph=%s)",
            vector_weight,
            sparse_weight,
            vector_store is not None,
            sparse_store is not None,
            sparse_fts_collection,
            graph_stage is not None,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def recall(
        self,
        query_vector: list[float],
        query_terms: list[str],
        query_text: str = "",
        plan: Any | None = None,
        scope_filter: dict[str, Any] | None = None,
    ) -> list[RecallResult]:
        """Execute hybrid retrieval under the given ``RetrievalPlan``.

        Args:
            query_vector: Dense embedding of the query.
            query_terms: Tokenised sparse query terms.
            query_text: Raw query string for FTS5 sparse path.
            plan: ``RetrievalPlan`` from L0.  replay_key / policy_hash are
                propagated to every result.  ``None`` → live mode, no metadata.
            scope_filter: Arbitrary key-value scope filter for the dense backend.

        Returns:
            Deduplicated, merged, sorted ``RecallResult`` list capped at top_k.
        """
        plan_id = plan.plan_id if plan is not None else "no_plan"
        replay_key = (plan.replay_key or "") if plan is not None else ""
        policy_hash = plan.policy_hash if plan is not None else ""
        effective_top_k = plan.top_k if plan is not None else self.top_k

        trace_id = f"recall_{plan_id}"
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L1_REASONING,
            "HybridRecallStage.recall",
        )

        # Determine retrieval mode (C0.2 mode dispatch)
        retrieval_mode = plan.retrieval_mode if plan is not None else RetrievalMode.HYBRID

        # C0.3 GRAPH mode — delegate to graph stage
        if retrieval_mode == RetrievalMode.GRAPH and self._graph_stage is not None:
            seed_path = scope_filter.get("file_path", "") if scope_filter else ""
            if seed_path:
                graph_results = self._graph_stage.recall(
                    seed_file_path=seed_path,
                    plan=plan,
                )
                for r in graph_results:
                    r.metadata["replay_key"] = replay_key
                    r.metadata["policy_hash"] = policy_hash
                    r.metadata["plan_id"] = plan_id
                log.debug("Graph recall [plan=%s]: graph=%d", plan_id, len(graph_results))
                return graph_results[:effective_top_k]
            log.debug("GRAPH mode but no seed file_path; falling through to hybrid")

        # C0.2 DENSE-only mode — skip sparse
        if retrieval_mode == RetrievalMode.DENSE:
            dense_results = self._dense_recall(query_vector, scope_filter)
            for r in dense_results:
                r.metadata["replay_key"] = replay_key
                r.metadata["policy_hash"] = policy_hash
                r.metadata["plan_id"] = plan_id
            log.debug("Dense-only recall [plan=%s]: dense=%d", plan_id, len(dense_results))
            return dense_results[:effective_top_k]

        # C0.2 SPARSE-only mode — skip dense
        if retrieval_mode == RetrievalMode.SPARSE:
            sparse_results = self._sparse_recall(
                query_terms,
                query_text or " ".join(query_terms),
                scope_filter,
            )
            for r in sparse_results:
                r.metadata["replay_key"] = replay_key
                r.metadata["policy_hash"] = policy_hash
                r.metadata["plan_id"] = plan_id
            log.debug("Sparse-only recall [plan=%s]: sparse=%d", plan_id, len(sparse_results))
            return sparse_results[:effective_top_k]

        # HYBRID (default) — run both and merge
        dense_results = self._dense_recall(query_vector, scope_filter)
        sparse_results = self._sparse_recall(
            query_terms,
            query_text or " ".join(query_terms),
            scope_filter,
        )
        merged = self._merge_results(dense_results, sparse_results)

        # Stamp replay / governance metadata onto every result
        for r in merged:
            r.metadata["replay_key"] = replay_key
            r.metadata["policy_hash"] = policy_hash
            r.metadata["plan_id"] = plan_id

        _emit_records_telemetry_event(
            trace_id,
            "hybrid_recall",
            f"d{len(dense_results)}_s{len(sparse_results)}_m{len(merged)}",
        )

        log.debug(
            "Hybrid recall [plan=%s]: dense=%d sparse=%d merged=%d",
            plan_id,
            len(dense_results),
            len(sparse_results),
            len(merged),
        )
        return merged[:effective_top_k]

    # ------------------------------------------------------------------
    # Dense path
    # ------------------------------------------------------------------

    def _dense_recall(
        self,
        query_vector: list[float],
        scope_filter: dict[str, Any] | None,
    ) -> list[RecallResult]:
        """Query the injected vector store; safe no-op when absent."""
        if self._vector_store is None:
            return []

        try:
            raw = self._vector_store.query(query_vector, self.top_k * 2, scope_filter)
        except (OSError, TypeError, ValueError, RuntimeError, AttributeError) as exc:
            log.warning("Dense recall failed: %s", exc)
            return []

        return [
            RecallResult(
                doc_id=item.get("id", ""),
                score=float(item.get("score", 0.0)),
                source="dense",
                content=item.get("content", ""),
                metadata=item.get("metadata", {}),
            )
            for item in raw
        ]

    # ------------------------------------------------------------------
    # Sparse path
    # ------------------------------------------------------------------

    def _sparse_recall(
        self,
        query_terms: list[str],
        query_text: str,
        scope_filter: dict[str, Any] | None,
    ) -> list[RecallResult]:
        """Query FTS5 SparseIndex (primary) then Bm25Store (fallback).

        Architecture reference: 00D §Sparse Path.
        """
        results: list[RecallResult] = []

        if self._sparse_fts_collection is not None:
            results.extend(self._fts_recall(query_text))

        if self._sparse_store is not None and query_terms:
            seen = {r.doc_id for r in results}
            for hit in self._bm25_recall(query_terms, query_text):
                if hit.doc_id not in seen:
                    results.append(hit)
                    seen.add(hit.doc_id)

        return results

    def _fts_recall(self, query_text: str) -> list[RecallResult]:
        """Query the FTS5-backed SparseIndex for the configured collection."""
        if self._sparse_fts_index is None:
            try:
                from agentic_core.L4_state.utils.memory.bm25_store import (  # noqa: PLC0415
                    get_sparse_index,
                )

                self._sparse_fts_index = get_sparse_index(self._sparse_fts_collection)
            except ImportError as exc:
                log.warning("SparseIndex import failed: %s", exc)
                return []

        if self._sparse_fts_index is None or not self._sparse_fts_index.is_available:
            return []

        try:
            raw = self._sparse_fts_index.search(query_text, top_k=self.top_k * 2)
        except (OSError, TypeError, AttributeError) as exc:
            log.warning("FTS5 sparse recall failed: %s", exc)
            return []

        return [
            RecallResult(
                doc_id=item["id"],
                score=float(item["score"]),
                source="sparse",
                content=item.get("content", ""),
                metadata=item.get("metadata", {}),
            )
            for item in raw
        ]

    def _bm25_recall(
        self,
        query_terms: list[str],
        query_text: str,
    ) -> list[RecallResult]:
        """Query the in-memory Bm25Store."""
        query = query_text or " ".join(query_terms)
        try:
            raw = self._sparse_store.query(query, top_k=self.top_k * 2)
        except (AttributeError, TypeError, ValueError) as exc:
            log.warning("Bm25Store recall failed: %s", exc)
            return []

        return [
            RecallResult(
                doc_id=item["id"],
                score=float(item["score"]),
                source="sparse",
                content=item.get("content", ""),
                metadata=item.get("metadata", {}),
            )
            for item in raw
        ]

    # ------------------------------------------------------------------
    # Hybrid merge — 00D §Hybrid Merge: sparse wins on IDs
    # ------------------------------------------------------------------

    def _merge_results(
        self,
        dense: list[RecallResult],
        sparse: list[RecallResult],
    ) -> list[RecallResult]:
        """Merge dense and sparse candidates.

        Rule (00D §Hybrid Merge):
          - Union of all doc IDs.
          - Sparse IDs are guaranteed to appear regardless of dense score.
          - Score: ``dense_score * vector_weight + sparse_score * sparse_weight``.
          - Content: sparse text preferred over dense when available.
          - Sort descending by final score.
        """
        dense_map: dict[str, RecallResult] = {r.doc_id: r for r in dense}
        sparse_map: dict[str, RecallResult] = {r.doc_id: r for r in sparse}

        merged: list[RecallResult] = []
        all_ids = set(dense_map) | set(sparse_map)
        for doc_id in tqdm(all_ids, desc="Merging recall results", unit="doc", leave=False):
            d = dense_map.get(doc_id)
            s = sparse_map.get(doc_id)

            d_score = d.score if d else 0.0
            s_score = s.score if s else 0.0
            hybrid_score = d_score * self.vector_weight + s_score * self.sparse_weight

            # Sparse content preferred (wins on IDs per 00D)
            content = (s.content if s and s.content else "") or (d.content if d else "")

            if d_score > 0 and s_score > 0:
                source = "both"
            elif s_score > 0:
                source = "sparse"
            else:
                source = "dense"

            merged.append(
                RecallResult(
                    doc_id=doc_id,
                    score=hybrid_score,
                    source=source,
                    content=content,
                    metadata={
                        "dense_score": d_score,
                        "sparse_score": s_score,
                    },
                )
            )

        merged.sort(key=lambda x: x.score, reverse=True)
        return merged


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_global_recall: HybridRecallStage | None = None


def get_hybrid_recall_stage() -> HybridRecallStage:
    """Get or create the global hybrid recall stage (no backends wired)."""
    global _global_recall
    if _global_recall is None:
        _global_recall = HybridRecallStage()
    return _global_recall
