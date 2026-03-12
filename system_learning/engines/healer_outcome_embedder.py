"""HealerOutcomeEmbedder — Semantic playbook memory for healer case retrieval.

Converts HealerOutcomeRecord objects into CorpusRecords for seed-pack ingestion
and provides nearest-neighbour retrieval over historical healer cases.

High-quality signal because the healer-validator architecture enforces lineage
and replay validation — healed cases are verified true positives.

Use cases:
  - Healer selection: retrieve successful healers for a given failure type
  - Failure clustering: group recurring patterns by semantic similarity
  - RCA assistance: find closest historical incident to a new failure

Design constraints:
- No wall-clock reads; all timestamps provided by caller.
- Deterministic text serialization via HealerOutcomeRecord.to_embedding_text().
- Kill-switch compliant: all retrieval paths check EMBEDDING_ENABLED.
- C0_INFORMATIONAL only: no routing influence from results.
- Thread-safe append via internal lock.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from typing import Any

from system_learning.engines.embedding_corpus_extraction import (
    CorpusRecord,
    compute_content_hash,
)
from system_learning.types.semantic_memory_types import HealerOutcomeRecord

logger = logging.getLogger(__name__)

_NAMESPACE = "healer_outcomes"


@dataclass(frozen=True)
class HealerRetrievalResult:
    """Nearest-neighbour result from healer outcome retrieval.

    C0_INFORMATIONAL only — no routing influence.
    """

    content_hash: str
    similarity_score: float
    healer_id: str
    failure_type: str
    outcome: str
    tier: str
    content_preview: str


class HealerOutcomeEmbedder:
    """Converts HealerOutcomeRecord objects to corpus records and retrieves similar cases.

    Usage:
        embedder = HealerOutcomeEmbedder()
        embedder.ingest(record)
        similar = embedder.retrieve_for_failure("IMPORT_ERROR: missing module x", k=5)
    """

    def __init__(self, max_buffer: int = 10_000) -> None:  # guardian: allow-magic_configuration
        if max_buffer < 1:
            raise ValueError(f"max_buffer must be >= 1, got {max_buffer}")
        self._max_buffer = max_buffer
        self._lock = threading.Lock()
        self._records: list[CorpusRecord] = []
        self._meta: dict[str, dict[str, Any]] = {}

    def ingest(self, record: HealerOutcomeRecord) -> CorpusRecord:
        """Convert a HealerOutcomeRecord to a CorpusRecord and buffer it.

        Args:
            record: The healer outcome record to ingest.

        Returns:
            The generated CorpusRecord.
        """
        text = record.to_embedding_text()
        content_hash = compute_content_hash(text.encode("utf-8"))
        corpus_record = CorpusRecord(
            text=text,
            trace_id=record.trace_id,
            content_hash=content_hash,
            namespace=_NAMESPACE,
        )
        meta = {
            "healer_id": record.healer_id,
            "failure_type": record.failure_type,
            "outcome": record.outcome,
            "tier": record.tier,
            "package_version": record.package_version,
            "outcome_hash": record.outcome_hash,
        }
        with self._lock:
            if len(self._records) >= self._max_buffer:
                dropped = self._records.pop(0)
                self._meta.pop(dropped.content_hash, None)
                logger.debug("HealerOutcomeEmbedder: buffer full, dropped oldest record")
            self._records.append(corpus_record)
            self._meta[content_hash] = meta
        return corpus_record

    def ingest_batch(self, records: list[HealerOutcomeRecord]) -> list[CorpusRecord]:
        """Ingest multiple HealerOutcomeRecords.

        Args:
            records: List of healer outcome records.

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
    ) -> list[HealerRetrievalResult]:
        """Retrieve healers that successfully handled similar failures.

        Primary use: healer selection — find the best historical healer
        for a new failure by semantic similarity to the violation text.

        Args:
            failure_text: The new failure description to match against.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of HealerRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(failure_text, k=k, namespace=namespace)

    def retrieve_similar(
        self,
        query_record: HealerOutcomeRecord,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[HealerRetrievalResult]:
        """Retrieve nearest-neighbour healer outcomes via sovereign semantic cache.

        Args:
            query_record: The outcome record to find neighbours for.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of HealerRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(query_record.to_embedding_text(), k=k, namespace=namespace)

    def _retrieve(
        self,
        query_text: str,
        *,
        k: int,
        namespace: str,
    ) -> list[HealerRetrievalResult]:
        k = min(k, 20)
        try:
            from agentic_core.interfaces.embeddings import query_similarity

            raw_results = query_similarity(query_text, top_k=k, namespace=namespace)
            out: list[HealerRetrievalResult] = []
            for r in raw_results:
                ch = r.content_hash
                meta = self._meta.get(ch, {})
                out.append(
                    HealerRetrievalResult(
                        content_hash=ch,
                        similarity_score=r.similarity_score,
                        healer_id=meta.get("healer_id", ""),
                        failure_type=meta.get("failure_type", ""),
                        outcome=meta.get("outcome", ""),
                        tier=meta.get("tier", ""),
                        content_preview=r.content_preview,
                    )
                )
            return out
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("HealerOutcomeEmbedder._retrieve: %s", exc)
            return []

    @staticmethod
    def record_from_healing_event(
        *,
        healer_id: str,
        failure_type: str,
        violation_text: str,
        fix_rationale: str,
        change_summary: str,
        package_version: str,
        outcome: str,
        tier: str,
        trace_id: str,
        timestamp_utc: int,
    ) -> HealerOutcomeRecord:
        """Convenience constructor that validates outcome literal."""
        if outcome not in ("success", "failure", "partial"):
            raise ValueError(f"outcome must be success/failure/partial, got {outcome!r}")
        return HealerOutcomeRecord(
            healer_id=healer_id,
            failure_type=failure_type,
            violation_text=violation_text,
            fix_rationale=fix_rationale,
            change_summary=change_summary,
            package_version=package_version,
            outcome=outcome,  # type: ignore[arg-type]
            tier=tier,
            trace_id=trace_id,
            timestamp_utc=timestamp_utc,
        )


__all__ = ["HealerOutcomeEmbedder", "HealerRetrievalResult"]
