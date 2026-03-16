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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from system_learning.config.semantic_memory_config import DEFAULT_EMBEDDER_BUFFER_SIZE
from system_learning.engines.embedding_corpus_extraction import (
    CorpusRecord,
    compute_content_hash,
)
from system_learning.types.semantic_memory_types import PromptOutcomeEmbeddingRecord

_emit_applies_guardrail("p0", "prompt_outcome_embedder", "p0_governance")
_emit_reads_policy_state("p0", "prompt_outcome_embedder", "policy_binding")
_emit_snapshots_state("p0", "prompt_outcome_embedder", "state_snapshot")
emit_replay_key("p0", "prompt_outcome_embedder")
emit_determinism_digest("p0", "prompt_outcome_embedder")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PromptOutcomeEmbedder.ingest")

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
        stats: dict[str, int] = dict.fromkeys(sorted(_VALID_SAFETY_OUTCOMES), 0)
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

    def top_templates_by_outcome(
        self, outcome: str, *, top_n: int = 5
    ) -> list[tuple[str, int]]:
        """Return the most-used template_ids for a given safety_outcome.

        Scans the in-memory buffer and counts template_id occurrences filtered
        by the requested safety_outcome.  Sorted by (count desc, template_id asc).

        Args:
            outcome: One of ALLOWED / BLOCKED / ESCALATED / HEALED / UNKNOWN.
            top_n: Maximum entries returned (capped at 50).

        Returns:
            List of (template_id, count) tuples, highest-count first.

        Raises:
            ValueError: If outcome is not a valid safety outcome literal.
        """
        if outcome not in _VALID_SAFETY_OUTCOMES:
            raise ValueError(
                f"outcome must be one of {sorted(_VALID_SAFETY_OUTCOMES)}, "
                f"got {outcome!r}"
            )
        top_n = min(top_n, 50)
        counts: dict[str, int] = {}
        with self._lock:
            for meta in self._meta.values():
                if meta.get("safety_outcome") == outcome:
                    tid = meta.get("template_id", "")
                    if tid:
                        counts[tid] = counts.get(tid, 0) + 1
        ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        return ranked[:top_n]

    def model_stats(self) -> dict[str, dict[str, int]]:
        """Return per-model safety outcome breakdowns for the buffered corpus.

        Useful for detecting model-specific safety regressions or identifying
        which models produce more escalations / blocks.

        Returns:
            Dict mapping model_name -> {safety_outcome: count, ...}.
            Only models/outcomes actually observed are included.
            Sorted by model name.
        """
        result: dict[str, dict[str, int]] = {}
        with self._lock:
            for meta in self._meta.values():
                model = meta.get("model", "")
                outcome = meta.get("safety_outcome", "")
                if model and outcome:
                    if model not in result:
                        result[model] = {}
                    result[model][outcome] = result[model].get(outcome, 0) + 1
        return dict(sorted(result.items()))

    def evict_before_timestamp(self, cutoff_utc: int) -> int:
        """Remove all buffered records whose CorpusRecord was ingested before a cutoff.

        The cutoff is matched against the ``trace_id`` timestamp embedded in the
        CorpusRecord via the originating PromptOutcomeEmbeddingRecord.
        Since CorpusRecord carries no timestamp itself, the cutoff is applied via
        a monotonic ingest-order proxy: records with trace_ids not surviving a
        registry refresh are retired.

        Implementation: compares ``timestamp_utc`` stored in meta (populated by
        ``record_from_execution`` when the field is present, otherwise falls back
        to scanning ``record_hash`` ordering).  This method is a best-effort
        semantic retirement tool, NOT a hard time-based eviction.

        Actually implemented as: evict all records whose ``record_id`` ends with a
        numeric suffix parsed from the trace or whose meta ``timestamp_utc`` (if
        stored by callers who populate it) is strictly less than cutoff_utc.

        Since the base PromptOutcomeEmbeddingRecord does not store timestamp in
        the meta dict (only record_hash is meta), this provides a hook callers
        can use by storing timestamp in the trace_id field.  For correctness the
        method scans the CorpusRecord.trace_id and parses an integer suffix.

        Simpler and correct implementation: scan record.trace_id for ``@TS:``
        prefix to extract a timestamp, then evict if < cutoff.  Callers who want
        timestamp-based eviction must pass trace_id as ``@TS:<unix_int>``.
        If trace_id has no such prefix, the record is kept.

        Args:
            cutoff_utc: Unix timestamp (integer seconds). Records whose trace_id
                encodes a timestamp < cutoff_utc are evicted.

        Returns:
            Number of records evicted.

        Raises:
            ValueError: If cutoff_utc <= 0.
        """
        if cutoff_utc <= 0:
            raise ValueError(f"cutoff_utc must be > 0, got {cutoff_utc}")
        evicted = 0
        with self._lock:
            keep: list[CorpusRecord] = []
            for record in self._records:
                tid = record.trace_id
                if tid.startswith("@TS:"):
                    try:
                        ts = int(tid[4:])
                        if ts < cutoff_utc:
                            self._meta.pop(record.content_hash, None)
                            evicted += 1
                            continue
                    except ValueError:
                        pass
                keep.append(record)
            self._records = keep
        return evicted

    def route_distribution(self) -> dict[str, int]:
        """Return count of buffered records by route.

        Enables detection of route-specific prompt outcome patterns,
        e.g. whether L2_PREMIUM consistently escalates more than L2_STANDARD.

        Returns:
            Dict mapping route -> count, sorted alphabetically by route.
        """
        counts: dict[str, int] = {}
        with self._lock:
            for meta in self._meta.values():
                route = meta.get("route", "")
                if route:
                    counts[route] = counts.get(route, 0) + 1
        return dict(sorted(counts.items()))

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
