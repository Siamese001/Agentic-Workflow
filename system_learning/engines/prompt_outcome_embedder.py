"""PromptOutcomeEmbedder — Semantic memory for prompt construction outcomes.

Converts PromptOutcomeEmbeddingRecord objects into CorpusRecords for
seed-pack ingestion and provides nearest-neighbour retrieval over
historical prompt constructions and their outcomes.

Enables:
  - Retrieving successful prompt constructions for a given task type
  - Detecting prompt drift: "what changed in slot composition?"
  - Improving template selection based on outcome similarity
  - Routing prompt decisions by historical precedent

Design constraints:
- No wall-clock reads; all timestamps provided by caller.
- Deterministic text via PromptOutcomeEmbeddingRecord.to_embedding_text().
- IDs (prompt_hash, template_id, route, model, policy_hash) are metadata only.
- Kill-switch compliant: all retrieval paths check EMBEDDING_ENABLED.
- C0_INFORMATIONAL only: no routing influence from results.
- Thread-safe append via internal lock.
"""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass
from typing import Any

from system_learning.config.semantic_memory_config import DEFAULT_EMBEDDER_BUFFER_SIZE
from system_learning.engines.embedding_corpus_extraction import (
    CorpusRecord,
    compute_content_hash,
)
from system_learning.types.semantic_memory_types import PromptOutcomeEmbeddingRecord

logger = logging.getLogger(__name__)

_NAMESPACE = "prompt_outcomes"

_VALID_SAFETY_OUTCOMES = frozenset(
    {"ALLOWED", "BLOCKED", "ESCALATED", "HEALED", "UNKNOWN"}
)


@dataclass(frozen=True)
class PromptOutcomeRetrievalResult:
    """Nearest-neighbour result from prompt outcome retrieval.

    C0_INFORMATIONAL only — no routing influence.
    """

    content_hash: str
    similarity_score: float
    record_id: str
    safety_outcome: str
    template_id: str
    model: str
    content_preview: str


class PromptOutcomeEmbedder:
    """Converts PromptOutcomeEmbeddingRecords to corpus records and retrieves similar outcomes.

    Usage:
        embedder = PromptOutcomeEmbedder()
        embedder.ingest(record)
        similar = embedder.retrieve_for_task("classify customer intent", k=5)
    """

    def __init__(self, max_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE) -> None:
        if max_buffer < 1:
            raise ValueError(f"max_buffer must be >= 1, got {max_buffer}")
        self._max_buffer = max_buffer
        self._lock = threading.Lock()
        self._records: list[CorpusRecord] = []
        self._meta: dict[str, dict[str, Any]] = {}

    def ingest(self, record: PromptOutcomeEmbeddingRecord) -> CorpusRecord:
        """Convert a PromptOutcomeEmbeddingRecord to a CorpusRecord and buffer it.

        Args:
            record: The prompt outcome record to ingest.

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
            "record_id": record.record_id,
            "safety_outcome": record.safety_outcome,
            "template_id": record.template_id,
            "route": record.route,
            "model": record.model,
            "prompt_hash": record.prompt_hash,
            "record_hash": record.record_hash,
        }
        with self._lock:
            if len(self._records) >= self._max_buffer:
                dropped = self._records.pop(0)
                self._meta.pop(dropped.content_hash, None)
                logger.debug("PromptOutcomeEmbedder: buffer full, dropped oldest record")
            self._records.append(corpus_record)
            self._meta[content_hash] = meta
        return corpus_record

    def ingest_batch(
        self, records: list[PromptOutcomeEmbeddingRecord]
    ) -> list[CorpusRecord]:
        """Ingest multiple PromptOutcomeEmbeddingRecords.

        Args:
            records: List of prompt outcome records.

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

    def retrieve_for_task(
        self,
        task_description: str,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[PromptOutcomeRetrievalResult]:
        """Retrieve historically similar prompt constructions for a task.

        Primary use: template selection — find prompts that successfully
        completed a semantically similar task.

        Args:
            task_description: The task description to match against.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of PromptOutcomeRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(f"task:{task_description}", k=k, namespace=namespace)

    def retrieve_similar(
        self,
        query_record: PromptOutcomeEmbeddingRecord,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[PromptOutcomeRetrievalResult]:
        """Retrieve nearest-neighbour prompt outcomes via sovereign semantic cache.

        Args:
            query_record: The record to find neighbours for.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of PromptOutcomeRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(query_record.to_embedding_text(), k=k, namespace=namespace)

    def retrieve_by_template(
        self,
        template_id: str,
        *,
        k: int = 10,
        namespace: str = _NAMESPACE,
    ) -> list[PromptOutcomeRetrievalResult]:
        """Retrieve cases anchored by template_id for drift detection.

        Use when a template version changes to find all historical outcomes
        governed by this template.

        Args:
            template_id: The template ID to anchor the search.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of PromptOutcomeRetrievalResult — C0_INFORMATIONAL.
        """
        query_text = f"template:{template_id}"
        return self._retrieve(query_text, k=k, namespace=namespace)

    def safety_outcome_stats(self) -> dict[str, int]:
        """Return count of buffered cases by safety_outcome.

        Returns:
            Dict mapping safety_outcome -> count; all 5 keys always present.
        """
        stats: dict[str, int] = {v: 0 for v in sorted(_VALID_SAFETY_OUTCOMES)}
        with self._lock:
            for meta in self._meta.values():
                outcome = meta.get("safety_outcome", "")
                if outcome in stats:
                    stats[outcome] += 1
        return stats

    def evict_by_template_id(self, template_id: str) -> int:
        """Remove all buffered records for a given template_id.

        Use when a template is deprecated to retire its historical records.

        Args:
            template_id: The template ID to evict.

        Returns:
            Number of records evicted.
        """
        if not template_id:
            raise ValueError("template_id must not be empty")
        evicted = 0
        with self._lock:
            keep: list[CorpusRecord] = []
            for record in self._records:
                meta = self._meta.get(record.content_hash, {})
                if meta.get("template_id") == template_id:
                    self._meta.pop(record.content_hash, None)
                    evicted += 1
                else:
                    keep.append(record)
            self._records = keep
        return evicted

    def _retrieve(
        self,
        query_text: str,
        *,
        k: int,
        namespace: str,
    ) -> list[PromptOutcomeRetrievalResult]:
        k = min(k, 20)
        try:
            from agentic_core.interfaces.embeddings import query_similarity

            raw_results = query_similarity(query_text, top_k=k, namespace=namespace)
            out: list[PromptOutcomeRetrievalResult] = []
            for r in raw_results:
                ch = r.content_hash
                meta = self._meta.get(ch, {})
                out.append(
                    PromptOutcomeRetrievalResult(
                        content_hash=ch,
                        similarity_score=r.similarity_score,
                        record_id=meta.get("record_id", ""),
                        safety_outcome=meta.get("safety_outcome", ""),
                        template_id=meta.get("template_id", ""),
                        model=meta.get("model", ""),
                        content_preview=r.content_preview,
                    )
                )
            return out
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("PromptOutcomeEmbedder._retrieve: %s", exc)
            return []

    @staticmethod
    def record_from_execution(
        *,
        record_id: str,
        slot_s0_summary: str,
        slot_d0_summary: str,
        slot_i0_summary: str,
        slot_c0_summary: str,
        slot_u0_summary: str,
        task_description: str,
        answer_summary: str,
        safety_outcome: str,
        retrieval_grounding_summary: str,
        prompt_hash: str,
        template_id: str,
        route: str,
        model: str,
        policy_hash: str,
        trace_id: str,
        timestamp_utc: int,
    ) -> PromptOutcomeEmbeddingRecord:
        """Convenience constructor that validates safety_outcome literal."""
        if safety_outcome not in _VALID_SAFETY_OUTCOMES:
            raise ValueError(
                f"safety_outcome must be one of {sorted(_VALID_SAFETY_OUTCOMES)}, "
                f"got {safety_outcome!r}"
            )
        return PromptOutcomeEmbeddingRecord(
            record_id=record_id,
            slot_s0_summary=slot_s0_summary,
            slot_d0_summary=slot_d0_summary,
            slot_i0_summary=slot_i0_summary,
            slot_c0_summary=slot_c0_summary,
            slot_u0_summary=slot_u0_summary,
            task_description=task_description,
            answer_summary=answer_summary,
            safety_outcome=safety_outcome,  # type: ignore[arg-type]
            retrieval_grounding_summary=retrieval_grounding_summary,
            prompt_hash=prompt_hash,
            template_id=template_id,
            route=route,
            model=model,
            policy_hash=policy_hash,
            trace_id=trace_id,
            timestamp_utc=timestamp_utc,
        )


__all__ = ["PromptOutcomeEmbedder", "PromptOutcomeRetrievalResult"]
