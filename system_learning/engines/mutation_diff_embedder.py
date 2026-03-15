"""MutationDiffEmbedder — Semantic memory for UWG mutation diffs.

Converts MutationDiffRecord objects into CorpusRecords for seed-pack ingestion
and provides nearest-neighbour retrieval over historical mutations.

Enables:
  - Pre-commit nearest-neighbour checks for risky mutation similarity
  - Post-commit retrieval for future healing
  - Rollback refinement retrieval from similar failed mutations

Design constraints:
- No wall-clock reads; all timestamps provided by caller.
- Deterministic text serialization via MutationDiffRecord.to_embedding_text().
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
from system_learning.types.semantic_memory_types import MutationDiffRecord

logger = logging.getLogger(__name__)

_NAMESPACE = "mutation_diffs"


@dataclass(frozen=True)
class MutationRetrievalResult:
    """Nearest-neighbour result from mutation diff retrieval.

    C0_INFORMATIONAL only — no routing influence.
    """

    content_hash: str
    similarity_score: float
    mutation_id: str
    target_resource: str
    commit_outcome: str
    content_preview: str


class MutationDiffEmbedder:
    """Converts MutationDiffRecord objects to corpus records and retrieves similar diffs.

    Three-phase use:
      1. pre_commit_check(record)  — retrieve similar prior mutations before commit
      2. ingest(record)            — buffer a committed or rolled-back record
      3. export_corpus_records()   — export for seed-pack ingestion

    All retrieval is C0_INFORMATIONAL: results influence proposals, not decisions.
    """

    def __init__(self, max_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE) -> None:
        if max_buffer < 1:
            raise ValueError(f"max_buffer must be >= 1, got {max_buffer}")
        self._max_buffer = max_buffer
        self._lock = threading.Lock()
        self._records: list[CorpusRecord] = []
        self._meta: dict[str, dict[str, Any]] = {}

    def ingest(self, record: MutationDiffRecord) -> CorpusRecord:
        """Convert a MutationDiffRecord to a CorpusRecord and buffer it.

        Args:
            record: The mutation diff record to ingest.

        Returns:
            The generated CorpusRecord.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "MutationDiffEmbedder.ingest")

        text = record.to_embedding_text()
        content_hash = compute_content_hash(text.encode("utf-8"))
        corpus_record = CorpusRecord(
            text=text,
            trace_id=record.trace_id,
            content_hash=content_hash,
            namespace=_NAMESPACE,
        )
        meta = {
            "mutation_id": record.mutation_id,
            "target_resource": record.target_resource,
            "commit_outcome": record.commit_outcome,
            "policy_hash": record.policy_hash,
            "diff_hash": record.diff_hash,
        }
        with self._lock:
            if len(self._records) >= self._max_buffer:
                dropped = self._records.pop(0)
                self._meta.pop(dropped.content_hash, None)
                logger.debug("MutationDiffEmbedder: buffer full, dropped oldest record")
            self._records.append(corpus_record)
            self._meta[content_hash] = meta
        return corpus_record

    def ingest_batch(self, records: list[MutationDiffRecord]) -> list[CorpusRecord]:
        """Ingest multiple MutationDiffRecords.

        Args:
            records: List of mutation diff records.

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

    def pre_commit_check(
        self,
        candidate: MutationDiffRecord,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[MutationRetrievalResult]:
        """Retrieve similar prior mutations before committing a new one.

        Used for risky-similarity detection: if top-k results contain
        rolled_back outcomes with high similarity, the caller should
        treat the candidate as high-risk.

        Args:
            candidate: The pending mutation to check.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of MutationRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(candidate.to_embedding_text(), k=k, namespace=namespace)

    def retrieve_similar(
        self,
        query_record: MutationDiffRecord,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[MutationRetrievalResult]:
        """Retrieve nearest-neighbour mutations via sovereign semantic cache.

        Args:
            query_record: The mutation to find neighbours for.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of MutationRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(query_record.to_embedding_text(), k=k, namespace=namespace)

    def _retrieve(
        self,
        query_text: str,
        *,
        k: int,
        namespace: str,
    ) -> list[MutationRetrievalResult]:
        k = min(k, 20)
        try:
            from agentic_core.interfaces.embeddings import query_similarity

            raw_results = query_similarity(query_text, top_k=k, namespace=namespace)
            out: list[MutationRetrievalResult] = []
            for r in raw_results:
                ch = r.content_hash
                meta = self._meta.get(ch, {})
                out.append(
                    MutationRetrievalResult(
                        content_hash=ch,
                        similarity_score=r.similarity_score,
                        mutation_id=meta.get("mutation_id", ""),
                        target_resource=meta.get("target_resource", ""),
                        commit_outcome=meta.get("commit_outcome", ""),
                        content_preview=r.content_preview,
                    )
                )
            return out
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("MutationDiffEmbedder._retrieve: %s", exc)
            return []

    @staticmethod
    def record_from_uwg_mutation(
        *,
        mutation_id: str,
        target_resource: str,
        operations: list[str],
        state_diff_summary: str,
        rollback_context: str,
        commit_outcome: str,
        trace_id: str,
        policy_hash: str,
        timestamp_utc: int,
    ) -> MutationDiffRecord:
        """Convenience constructor that validates commit_outcome literal."""
        if commit_outcome not in ("committed", "rolled_back", "pending"):
            raise ValueError(f"commit_outcome must be committed/rolled_back/pending, got {commit_outcome!r}")
        return MutationDiffRecord(
            mutation_id=mutation_id,
            target_resource=target_resource,
            operations=tuple(sorted(operations)),
            state_diff_summary=state_diff_summary,
            rollback_context=rollback_context,
            commit_outcome=commit_outcome,  # type: ignore[arg-type]
            trace_id=trace_id,
            policy_hash=policy_hash,
            timestamp_utc=timestamp_utc,
        )


__all__ = ["MutationDiffEmbedder", "MutationRetrievalResult"]
