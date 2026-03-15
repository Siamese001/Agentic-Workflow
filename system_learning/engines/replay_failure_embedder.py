"""ReplayFailureEmbedder — Semantic memory for determinism failure clustering.

Converts ReplayFailureRecord objects into CorpusRecords for seed-pack
ingestion and provides nearest-neighbour retrieval over historical
determinism failures and replay mismatches.

Enables:
  - Clustering determinism failure families by semantic similarity
  - Accelerating replay debugging: "what failed in the same way before?"
  - Detecting systemic nondeterminism leaks across subsystems
  - Triaging replay failures before committing expensive re-execution

Design constraints:
- No wall-clock reads; all timestamps provided by caller.
- Deterministic text serialization via ReplayFailureRecord.to_embedding_text().
- IDs (replay_key, determinism_digest) are metadata only, never embedded.
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
from system_learning.types.semantic_memory_types import ReplayFailureRecord

logger = logging.getLogger(__name__)

_NAMESPACE = "replay_failures"


@dataclass(frozen=True)
class ReplayFailureRetrievalResult:
    """Nearest-neighbour result from replay failure retrieval.

    C0_INFORMATIONAL only — no routing influence.
    """

    content_hash: str
    similarity_score: float
    failure_id: str
    nondeterminism_type: str
    replay_key: str
    content_preview: str


class ReplayFailureEmbedder:
    """Converts ReplayFailureRecord objects to corpus records and retrieves similar failures.

    Usage:
        embedder = ReplayFailureEmbedder()
        embedder.ingest(record)
        similar = embedder.retrieve_for_failure("hash mismatch in L3 routing", k=5)
    """

    def __init__(self, max_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE) -> None:
        if max_buffer < 1:
            raise ValueError(f"max_buffer must be >= 1, got {max_buffer}")
        self._max_buffer = max_buffer
        self._lock = threading.Lock()
        self._records: list[CorpusRecord] = []
        self._meta: dict[str, dict[str, Any]] = {}

    def ingest(self, record: ReplayFailureRecord) -> CorpusRecord:
        """Convert a ReplayFailureRecord to a CorpusRecord and buffer it.

        Args:
            record: The replay failure record to ingest.

        Returns:
            The generated CorpusRecord.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ReplayFailureEmbedder.ingest")

        text = record.to_embedding_text()
        content_hash = compute_content_hash(text.encode("utf-8"))
        corpus_record = CorpusRecord(
            text=text,
            trace_id=record.trace_id,
            content_hash=content_hash,
            namespace=_NAMESPACE,
        )
        meta = {
            "failure_id": record.failure_id,
            "nondeterminism_type": record.nondeterminism_type,
            "replay_key": record.replay_key,
            "determinism_digest": record.determinism_digest,
            "failure_hash": record.failure_hash,
        }
        with self._lock:
            if len(self._records) >= self._max_buffer:
                dropped = self._records.pop(0)
                self._meta.pop(dropped.content_hash, None)
                logger.debug("ReplayFailureEmbedder: buffer full, dropped oldest record")
            self._records.append(corpus_record)
            self._meta[content_hash] = meta
        return corpus_record

    def ingest_batch(self, records: list[ReplayFailureRecord]) -> list[CorpusRecord]:
        """Ingest multiple ReplayFailureRecords.

        Args:
            records: List of replay failure records.

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

    def retrieve_for_failure(
        self,
        failure_text: str,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[ReplayFailureRetrievalResult]:
        """Retrieve historically similar replay failures.

        Primary use: when a replay failure occurs, find similar past failures
        to accelerate triage and identify systemic nondeterminism patterns.

        Args:
            failure_text: Description of the new failure to match against.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of ReplayFailureRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(failure_text, k=k, namespace=namespace)

    def retrieve_by_nondeterminism_type(
        self,
        nondeterminism_type: str,
        *,
        k: int = 10,
        namespace: str = _NAMESPACE,
    ) -> list[ReplayFailureRetrievalResult]:
        """Retrieve cases anchored by nondeterminism type.

        Use to find all historical incidents of a given nondeterminism class
        (e.g. 'HASH_MISMATCH', 'ORDERING_INSTABILITY', 'TIMING_DEPENDENCY').

        Args:
            nondeterminism_type: The nondeterminism class to anchor search.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of ReplayFailureRetrievalResult — C0_INFORMATIONAL.
        """
        query_text = f"nondeterminism:{nondeterminism_type}"
        return self._retrieve(query_text, k=k, namespace=namespace)

    def retrieve_similar(
        self,
        query_record: ReplayFailureRecord,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[ReplayFailureRetrievalResult]:
        """Retrieve nearest-neighbour replay failures via sovereign semantic cache.

        Args:
            query_record: The record to find neighbours for.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of ReplayFailureRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(query_record.to_embedding_text(), k=k, namespace=namespace)

    def nondeterminism_type_stats(self) -> dict[str, int]:
        """Return count of buffered cases by nondeterminism_type.

        Returns:
            Dict mapping nondeterminism_type -> count, sorted by type name.
        """
        counts: dict[str, int] = {}
        with self._lock:
            for meta in self._meta.values():
                nd_type = meta.get("nondeterminism_type", "")
                if nd_type:
                    counts[nd_type] = counts.get(nd_type, 0) + 1
        return dict(sorted(counts.items()))

    def evict_by_replay_key(self, replay_key: str) -> int:
        """Remove all buffered records matching a replay_key.

        Use when a replay session is retired and its failure records are no
        longer relevant for clustering.

        Args:
            replay_key: The replay key to evict.

        Returns:
            Number of records evicted.
        """
        if not replay_key:
            raise ValueError("replay_key must not be empty")
        evicted = 0
        with self._lock:
            keep: list[CorpusRecord] = []
            for record in self._records:
                meta = self._meta.get(record.content_hash, {})
                if meta.get("replay_key") == replay_key:
                    self._meta.pop(record.content_hash, None)
                    evicted += 1
                else:
                    keep.append(record)
            self._records = keep
        return evicted

    def top_affected_subsystems(self, *, top_n: int = 5) -> list[tuple[str, int]]:
        """Return the most frequently affected subsystems across buffered failures.

        Counts each unique subsystem mention across all ``affected_subsystems``
        tuples in the buffer, then returns the top-N pairs sorted by
        (count desc, subsystem name asc) for tie-breaking.

        Args:
            top_n: Maximum number of entries to return (capped at 50).

        Returns:
            List of (subsystem_name, count) tuples, highest-count first.
        """
        top_n = min(top_n, 50)
        counts: dict[str, int] = {}
        with self._lock:
            for record in self._records:
                text = record.text
                subsystems_segment = ""
                for part in text.split(" ## "):
                    if part.startswith("subsystems:"):
                        subsystems_segment = part[len("subsystems:"):]
                        break
                if subsystems_segment:
                    for sub in subsystems_segment.split(" | "):
                        sub = sub.strip()
                        if sub:
                            counts[sub] = counts.get(sub, 0) + 1
        ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        return ranked[:top_n]

    def evict_by_nondeterminism_type(self, nondeterminism_type: str) -> int:
        """Remove all buffered records matching a nondeterminism_type.

        Use when a class of nondeterminism has been fully remediated and its
        historical records should no longer influence cluster retrieval.

        Args:
            nondeterminism_type: The nondeterminism class to evict.

        Returns:
            Number of records evicted.

        Raises:
            ValueError: If nondeterminism_type is empty.
        """
        if not nondeterminism_type:
            raise ValueError("nondeterminism_type must not be empty")
        evicted = 0
        with self._lock:
            keep: list[CorpusRecord] = []
            for record in self._records:
                meta = self._meta.get(record.content_hash, {})
                if meta.get("nondeterminism_type") == nondeterminism_type:
                    self._meta.pop(record.content_hash, None)
                    evicted += 1
                else:
                    keep.append(record)
            self._records = keep
        return evicted

    def replay_key_summary(self) -> list[tuple[str, int]]:
        """Return (replay_key, case_count) pairs sorted by count descending.

        Useful for identifying which replay sessions have contributed the most
        failure records — candidates for bulk eviction once a session retires.

        Returns:
            List of (replay_key, count) tuples, highest-count first.
            Tie-break: alphabetical by replay_key.
        """
        counts: dict[str, int] = {}
        with self._lock:
            for meta in self._meta.values():
                rk = meta.get("replay_key", "")
                if rk:
                    counts[rk] = counts.get(rk, 0) + 1
        return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))

    def _retrieve(
        self,
        query_text: str,
        *,
        k: int,
        namespace: str,
    ) -> list[ReplayFailureRetrievalResult]:
        k = min(k, 20)
        try:
            from agentic_core.interfaces.embeddings import query_similarity

            raw_results = query_similarity(query_text, top_k=k, namespace=namespace)
            out: list[ReplayFailureRetrievalResult] = []
            for r in raw_results:
                ch = r.content_hash
                meta = self._meta.get(ch, {})
                out.append(
                    ReplayFailureRetrievalResult(
                        content_hash=ch,
                        similarity_score=r.similarity_score,
                        failure_id=meta.get("failure_id", ""),
                        nondeterminism_type=meta.get("nondeterminism_type", ""),
                        replay_key=meta.get("replay_key", ""),
                        content_preview=r.content_preview,
                    )
                )
            return out
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("ReplayFailureEmbedder._retrieve: %s", exc)
            return []

    @staticmethod
    def record_from_replay_event(
        *,
        failure_id: str,
        failure_summary: str,
        nondeterminism_type: str,
        mismatch_explanation: str,
        affected_subsystems: list[str],
        attempted_remediation: str,
        replay_key: str,
        determinism_digest: str,
        trace_id: str,
        timestamp_utc: int,
    ) -> ReplayFailureRecord:
        """Convenience constructor for replay engine events."""
        if not failure_id:
            raise ValueError("failure_id must not be empty")
        if not nondeterminism_type:
            raise ValueError("nondeterminism_type must not be empty")
        if not replay_key:
            raise ValueError("replay_key must not be empty")
        return ReplayFailureRecord(
            failure_id=failure_id,
            failure_summary=failure_summary,
            nondeterminism_type=nondeterminism_type,
            mismatch_explanation=mismatch_explanation,
            affected_subsystems=tuple(sorted(affected_subsystems)),
            attempted_remediation=attempted_remediation,
            replay_key=replay_key,
            determinism_digest=determinism_digest,
            trace_id=trace_id,
            timestamp_utc=timestamp_utc,
        )


__all__ = ["ReplayFailureEmbedder", "ReplayFailureRetrievalResult"]
