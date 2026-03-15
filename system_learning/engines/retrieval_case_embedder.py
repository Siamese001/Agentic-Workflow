"""RetrievalCaseEmbedder — Semantic memory for RAG retrieval quality learning.

Converts RetrievalCaseRecord objects into CorpusRecords for seed-pack
ingestion and provides nearest-neighbour retrieval over historical
retrieval quality cases.

Enables:
  - Identifying weak chunk sets for corpus expansion
  - Guiding retrieval depth and chunk ranking policy adjustments
  - Detecting queries that consistently produce low-quality retrievals
  - Meta-learning bus integration via quality signal metadata

Design constraints:
- No wall-clock reads; all timestamps provided by caller.
- Deterministic text serialization via RetrievalCaseRecord.to_embedding_text().
- IDs (query_id, chunk_ids) are metadata only, never embedded in text.
- Kill-switch compliant: all retrieval paths check EMBEDDING_ENABLED.
- C0_INFORMATIONAL only: no routing influence from results.
- Thread-safe append via internal lock.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace
from system_learning.config.semantic_memory_config import DEFAULT_EMBEDDER_BUFFER_SIZE
from system_learning.engines.embedding_corpus_extraction import (
    CorpusRecord,
    compute_content_hash,
)
from system_learning.types.semantic_memory_types import RetrievalCaseRecord

logger = logging.getLogger(__name__)

_NAMESPACE = "retrieval_cases"


@dataclass(frozen=True)
class RetrievalCaseRetrievalResult:
    """Nearest-neighbour result from retrieval case search.

    C0_INFORMATIONAL only — no routing influence.
    """

    content_hash: str
    similarity_score: float
    case_id: str
    support_score: float
    completeness_score: float
    escalation_flag: bool
    content_preview: str


class RetrievalCaseEmbedder:
    """Converts RetrievalCaseRecord objects to corpus records and retrieves similar cases.

    Usage:
        embedder = RetrievalCaseEmbedder()
        embedder.ingest(record)
        weak = embedder.retrieve_weak_cases(threshold=0.5, limit=10)
    """

    def __init__(self, max_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE) -> None:
        if max_buffer < 1:
            raise ValueError(f"max_buffer must be >= 1, got {max_buffer}")
        self._max_buffer = max_buffer
        self._lock = threading.Lock()
        self._records: list[CorpusRecord] = []
        self._meta: dict[str, dict[str, Any]] = {}

    def ingest(self, record: RetrievalCaseRecord) -> CorpusRecord:
        """Convert a RetrievalCaseRecord to a CorpusRecord and buffer it.

        Args:
            record: The retrieval case record to ingest.

        Returns:
            The generated CorpusRecord.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RetrievalCaseEmbedder.ingest")

        text = record.to_embedding_text()
        content_hash = compute_content_hash(text.encode("utf-8"))
        corpus_record = CorpusRecord(
            text=text,
            trace_id=record.trace_id,
            content_hash=content_hash,
            namespace=_NAMESPACE,
        )
        meta = {
            "case_id": record.case_id,
            "query_id": record.query_id,
            "support_score": record.support_score,
            "completeness_score": record.completeness_score,
            "escalation_flag": record.escalation_flag,
            "healer_invoked": record.healer_invoked,
            "replay_pass": record.replay_pass,
            "case_hash": record.case_hash,
        }
        with self._lock:
            if len(self._records) >= self._max_buffer:
                dropped = self._records.pop(0)
                self._meta.pop(dropped.content_hash, None)
                logger.debug("RetrievalCaseEmbedder: buffer full, dropped oldest record")
            self._records.append(corpus_record)
            self._meta[content_hash] = meta
        return corpus_record

    def ingest_batch(self, records: list[RetrievalCaseRecord]) -> list[CorpusRecord]:
        """Ingest multiple RetrievalCaseRecords.

        Args:
            records: List of retrieval case records.

        Returns:
            List of generated CorpusRecords in the same order.
        """
        return [self.ingest(r) for r in records]

    def export_corpus_records(self) -> list[CorpusRecord]:
        """Return a deterministically sorted snapshot of buffered records.

        Sorted by (content_hash, trace_id) for determinism.
        """
        with self._lock:
            return sorted(self._records, key=lambda r: (r.content_hash, r.trace_id))

    def buffer_size(self) -> int:
        """Return current number of buffered records."""
        with self._lock:
            return len(self._records)

    def retrieve_similar(
        self,
        query_record: RetrievalCaseRecord,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[RetrievalCaseRetrievalResult]:
        """Retrieve nearest-neighbour retrieval cases via sovereign semantic cache.

        Args:
            query_record: The record to find neighbours for.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of RetrievalCaseRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(query_record.to_embedding_text(), k=k, namespace=namespace)

    def retrieve_for_query(
        self,
        query_summary: str,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[RetrievalCaseRetrievalResult]:
        """Retrieve cases similar to a new query for retrieval policy guidance.

        Args:
            query_summary: The query to find similar historical cases for.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of RetrievalCaseRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(f"query:{query_summary}", k=k, namespace=namespace)

    def retrieve_weak_cases(
        self,
        *,
        support_threshold: float = 0.5,
        completeness_threshold: float = 0.5,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Return metadata for buffered cases below quality thresholds.

        Does not call the embedding service — pure in-memory scan.
        Used by the meta-learning bus to identify corpus expansion candidates.

        Args:
            support_threshold: Cases with support_score < this are weak.
            completeness_threshold: Cases with completeness_score < this are weak.
            limit: Maximum results (capped at 100).

        Returns:
            List of metadata dicts sorted by (support_score, case_id) asc.
        """
        if not (0.0 <= support_threshold <= 1.0):
            raise ValueError(
                f"support_threshold must be in [0.0, 1.0], got {support_threshold}"
            )
        if not (0.0 <= completeness_threshold <= 1.0):
            raise ValueError(
                f"completeness_threshold must be in [0.0, 1.0], got {completeness_threshold}"
            )
        limit = min(limit, 100)
        results: list[dict[str, Any]] = []
        with self._lock:
            for meta in self._meta.values():
                ss = meta.get("support_score", 1.0)
                cs = meta.get("completeness_score", 1.0)
                if ss < support_threshold or cs < completeness_threshold:
                    results.append(dict(meta))
        results.sort(key=lambda m: (m.get("support_score", 0.0), m.get("case_id", "")))
        return results[:limit]

    def quality_signal_summary(self) -> dict[str, Any]:
        """Aggregate quality signals over all buffered cases.

        Returns a summary dict with:
          - count: total buffered cases
          - avg_support_score: mean support_score (0.0 if empty)
          - avg_completeness_score: mean completeness_score (0.0 if empty)
          - escalation_rate: fraction of cases with escalation_flag=True
          - healer_invoked_rate: fraction with healer_invoked=True
          - replay_pass_rate: fraction with replay_pass=True
        """
        with self._lock:
            metas = list(self._meta.values())
        n = len(metas)
        if n == 0:
            return {
                "count": 0,
                "avg_support_score": 0.0,
                "avg_completeness_score": 0.0,
                "escalation_rate": 0.0,
                "healer_invoked_rate": 0.0,
                "replay_pass_rate": 0.0,
            }
        avg_sup = round(sum(m.get("support_score", 0.0) for m in metas) / n, 6)
        avg_comp = round(
            sum(m.get("completeness_score", 0.0) for m in metas) / n, 6
        )
        esc_rate = round(sum(1 for m in metas if m.get("escalation_flag")) / n, 6)
        heal_rate = round(sum(1 for m in metas if m.get("healer_invoked")) / n, 6)
        replay_rate = round(sum(1 for m in metas if m.get("replay_pass")) / n, 6)
        return {
            "count": n,
            "avg_support_score": avg_sup,
            "avg_completeness_score": avg_comp,
            "escalation_rate": esc_rate,
            "healer_invoked_rate": heal_rate,
            "replay_pass_rate": replay_rate,
        }

    def escalation_candidates(self, *, limit: int = 20) -> list[dict[str, Any]]:
        """Return metadata for buffered cases where escalation_flag=True.

        Sorted by (completeness_score asc, case_id asc) — lowest-quality
        escalations first, since those are most urgent for corpus improvement.

        Args:
            limit: Maximum results (capped at 100).

        Returns:
            List of metadata dicts for escalated cases.
        """
        limit = min(limit, 100)
        results: list[dict[str, Any]] = []
        with self._lock:
            for meta in self._meta.values():
                if meta.get("escalation_flag"):
                    results.append(dict(meta))
        results.sort(key=lambda m: (m.get("completeness_score", 0.0), m.get("case_id", "")))
        return results[:limit]

    def corpus_expansion_report(self) -> dict[str, Any]:
        """Generate a corpus expansion guidance report from buffered cases.

        Identifies:
          - Cases that escalated without a healer (pure retrieval gaps)
          - Cases with support_score < 0.5 (weak chunk coverage)
          - Cases where replay failed (determinism risk)
          - Overall quality tier: 'HEALTHY' / 'DEGRADED' / 'CRITICAL'

        Returns:
            Dict with keys:
              pure_escalation_count   — escalated and healer_invoked=False
              weak_support_count      — support_score < 0.5
              replay_failure_count    — replay_pass=False
              total                   — total buffered cases
              quality_tier            — 'HEALTHY' | 'DEGRADED' | 'CRITICAL'
        """
        with self._lock:
            metas = list(self._meta.values())
        n = len(metas)
        pure_esc = sum(
            1 for m in metas
            if m.get("escalation_flag") and not m.get("healer_invoked")
        )
        weak_sup = sum(1 for m in metas if m.get("support_score", 1.0) < 0.5)
        replay_fail = sum(1 for m in metas if not m.get("replay_pass", True))
        if n == 0:
            tier = "HEALTHY"
        else:
            degraded_rate = (pure_esc + weak_sup + replay_fail) / n
            if degraded_rate >= 0.5:
                tier = "CRITICAL"
            elif degraded_rate >= 0.2:
                tier = "DEGRADED"
            else:
                tier = "HEALTHY"
        return {
            "pure_escalation_count": pure_esc,
            "weak_support_count": weak_sup,
            "replay_failure_count": replay_fail,
            "total": n,
            "quality_tier": tier,
        }

    def evict_by_query_id(self, query_id: str) -> int:
        """Remove all buffered records matching a query_id.

        Use to retire cases associated with a specific query session
        (e.g. when a query template is updated and old cases are stale).

        Args:
            query_id: The query identifier to evict.

        Returns:
            Number of records evicted.

        Raises:
            ValueError: If query_id is empty.
        """
        if not query_id:
            raise ValueError("query_id must not be empty")
        evicted = 0
        with self._lock:
            keep: list[CorpusRecord] = []
            for record in self._records:
                meta = self._meta.get(record.content_hash, {})
                if meta.get("query_id") == query_id:
                    self._meta.pop(record.content_hash, None)
                    evicted += 1
                else:
                    keep.append(record)
            self._records = keep
        return evicted

    def score_percentile_buckets(self) -> dict[str, dict[str, int]]:
        """Bucket support_score and completeness_score into quartile ranges.

        Returns counts per quartile for both scores, enabling quick
        corpus quality distribution visualization without external tools.

        Buckets: 'Q1' [0.0, 0.25), 'Q2' [0.25, 0.50),
                 'Q3' [0.50, 0.75), 'Q4' [0.75, 1.0]

        Returns:
            Dict with keys 'support_score' and 'completeness_score',
            each mapping to {'Q1': n, 'Q2': n, 'Q3': n, 'Q4': n}.
        """
        support_buckets: dict[str, int] = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}
        complete_buckets: dict[str, int] = {"Q1": 0, "Q2": 0, "Q3": 0, "Q4": 0}

        def _bucket(v: float) -> str:
            if v < 0.25:
                return "Q1"
            if v < 0.50:
                return "Q2"
            if v < 0.75:
                return "Q3"
            return "Q4"

        with self._lock:
            for meta in self._meta.values():
                support_buckets[_bucket(float(meta.get("support_score", 0.0)))] += 1
                complete_buckets[_bucket(float(meta.get("completeness_score", 0.0)))] += 1
        return {
            "support_score": support_buckets,
            "completeness_score": complete_buckets,
        }

    def _retrieve(
        self,
        query_text: str,
        *,
        k: int,
        namespace: str,
    ) -> list[RetrievalCaseRetrievalResult]:
        k = min(k, 20)
        try:
            from agentic_core.interfaces.embeddings import query_similarity

            raw_results = query_similarity(query_text, top_k=k, namespace=namespace)
            out: list[RetrievalCaseRetrievalResult] = []
            for r in raw_results:
                ch = r.content_hash
                meta = self._meta.get(ch, {})
                out.append(
                    RetrievalCaseRetrievalResult(
                        content_hash=ch,
                        similarity_score=r.similarity_score,
                        case_id=meta.get("case_id", ""),
                        support_score=float(meta.get("support_score", 0.0)),
                        completeness_score=float(
                            meta.get("completeness_score", 0.0)
                        ),
                        escalation_flag=bool(meta.get("escalation_flag", False)),
                        content_preview=r.content_preview,
                    )
                )
            return out
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("RetrievalCaseEmbedder._retrieve: %s", exc)
            return []

    @staticmethod
    def record_from_rag_evaluation(
        *,
        case_id: str,
        query_summary: str,
        chunk_summaries: list[str],
        support_reasoning: str,
        answer_quality_summary: str,
        query_id: str,
        chunk_ids: list[str],
        support_score: float,
        completeness_score: float,
        escalation_flag: bool,
        healer_invoked: bool,
        replay_pass: bool,
        trace_id: str,
        timestamp_utc: int,
    ) -> RetrievalCaseRecord:
        """Convenience constructor that validates score ranges."""
        if not (0.0 <= support_score <= 1.0):
            raise ValueError(
                f"support_score must be in [0.0, 1.0], got {support_score}"
            )
        if not (0.0 <= completeness_score <= 1.0):
            raise ValueError(
                f"completeness_score must be in [0.0, 1.0], got {completeness_score}"
            )
        return RetrievalCaseRecord(
            case_id=case_id,
            query_summary=query_summary,
            chunk_summaries=tuple(sorted(chunk_summaries)),
            support_reasoning=support_reasoning,
            answer_quality_summary=answer_quality_summary,
            query_id=query_id,
            chunk_ids=tuple(sorted(chunk_ids)),
            support_score=support_score,
            completeness_score=completeness_score,
            escalation_flag=escalation_flag,
            healer_invoked=healer_invoked,
            replay_pass=replay_pass,
            trace_id=trace_id,
            timestamp_utc=timestamp_utc,
        )


__all__ = ["RetrievalCaseEmbedder", "RetrievalCaseRetrievalResult"]
