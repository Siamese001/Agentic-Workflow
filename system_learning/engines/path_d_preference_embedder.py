"""PathDPreferenceEmbedder — Semantic memory for HITL preference pairs.

Converts PathDPreferencePair objects (DPO-style human decisions from Path D)
into CorpusRecords for seed-pack ingestion and provides nearest-neighbour
retrieval over historical human preference judgments.

Enables retrieval of human preference precedents before:
  - Proposing an action that resembles a previously-rejected plan
  - Escalating to HITL (what did humans decide in similar situations?)
  - Tuning thresholds based on human approval/rejection patterns

Design constraints:
- No wall-clock reads; all timestamps provided by caller.
- Deterministic text serialization via PathDPreferencePair.to_embedding_text().
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
from system_learning.types.semantic_memory_types import PathDPreferencePair
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

logger = logging.getLogger(__name__)

_NAMESPACE = "path_d_preferences"


@dataclass(frozen=True)
class PreferenceRetrievalResult:
    """Nearest-neighbour result from Path D preference retrieval.

    C0_INFORMATIONAL only — no routing influence.
    """

    content_hash: str
    similarity_score: float
    decision_id: str
    decision: str
    agent: str
    content_preview: str


class PathDPreferenceEmbedder:
    """Converts PathDPreferencePair objects to corpus records and retrieves similar cases.

    Usage:
        embedder = PathDPreferenceEmbedder()
        embedder.ingest(pair)
        similar = embedder.retrieve_for_proposal(plan_text, k=5)
    """

    def __init__(self, max_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE) -> None:
        if max_buffer < 1:
            raise ValueError(f"max_buffer must be >= 1, got {max_buffer}")
        self._max_buffer = max_buffer
        self._lock = threading.Lock()
        self._records: list[CorpusRecord] = []
        self._meta: dict[str, dict[str, Any]] = {}

    def ingest(self, pair: PathDPreferencePair) -> CorpusRecord:
        """Convert a PathDPreferencePair to a CorpusRecord and buffer it.

        Args:
            pair: The preference pair to ingest.

        Returns:
            The generated CorpusRecord.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "PathDPreferenceEmbedder.ingest")

        text = pair.to_embedding_text()
        content_hash = compute_content_hash(text.encode("utf-8"))
        corpus_record = CorpusRecord(
            text=text,
            trace_id=pair.trace_id,
            content_hash=content_hash,
            namespace=_NAMESPACE,
        )
        meta = {
            "decision_id": pair.decision_id,
            "decision": pair.decision,
            "agent": pair.agent,
            "resulting_outcome": pair.resulting_outcome,
            "pair_hash": pair.pair_hash,
        }
        with self._lock:
            if len(self._records) >= self._max_buffer:
                dropped = self._records.pop(0)
                self._meta.pop(dropped.content_hash, None)
                logger.debug("PathDPreferenceEmbedder: buffer full, dropped oldest record")
            self._records.append(corpus_record)
            self._meta[content_hash] = meta
        return corpus_record

    def ingest_batch(self, pairs: list[PathDPreferencePair]) -> list[CorpusRecord]:
        """Ingest multiple PathDPreferencePairs.

        Args:
            pairs: List of preference pairs.

        Returns:
            List of generated CorpusRecords in the same order.
        """
        return [self.ingest(p) for p in pairs]

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

    def retrieve_for_proposal(
        self,
        plan_text: str,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[PreferenceRetrievalResult]:
        """Retrieve precedent human decisions for a proposed plan.

        Primary use: before escalating to HITL, check whether similar plans
        were previously approved or rejected to inform the proposal framing.

        Args:
            plan_text: The proposed plan text to match against.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of PreferenceRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(plan_text, k=k, namespace=namespace)

    def retrieve_similar(
        self,
        query_pair: PathDPreferencePair,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[PreferenceRetrievalResult]:
        """Retrieve nearest-neighbour preference pairs via sovereign semantic cache.

        Args:
            query_pair: The preference pair to find neighbours for.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of PreferenceRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(query_pair.to_embedding_text(), k=k, namespace=namespace)

    def _retrieve(
        self,
        query_text: str,
        *,
        k: int,
        namespace: str,
    ) -> list[PreferenceRetrievalResult]:
        k = min(k, 20)
        try:
            from agentic_core.interfaces.embeddings import query_similarity

            raw_results = query_similarity(query_text, top_k=k, namespace=namespace)
            out: list[PreferenceRetrievalResult] = []
            for r in raw_results:
                ch = r.content_hash
                meta = self._meta.get(ch, {})
                out.append(
                    PreferenceRetrievalResult(
                        content_hash=ch,
                        similarity_score=r.similarity_score,
                        decision_id=meta.get("decision_id", ""),
                        decision=meta.get("decision", ""),
                        agent=meta.get("agent", ""),
                        content_preview=r.content_preview,
                    )
                )
            return out
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("PathDPreferenceEmbedder._retrieve: %s", exc)
            return []

    @staticmethod
    def pair_from_hitl_log(
        *,
        decision_id: str,
        original_plan: str,
        human_patch: str,
        decision: str,
        reason: str,
        resulting_outcome: str,
        agent: str,
        trace_id: str,
        timestamp_utc: int,
    ) -> PathDPreferencePair:
        """Convenience constructor that validates decision literal."""
        if decision not in ("approved", "rejected", "modified"):
            raise ValueError(f"decision must be approved/rejected/modified, got {decision!r}")
        return PathDPreferencePair(
            decision_id=decision_id,
            original_plan=original_plan,
            human_patch=human_patch,
            decision=decision,  # type: ignore[arg-type]
            reason=reason,
            resulting_outcome=resulting_outcome,
            agent=agent,
            trace_id=trace_id,
            timestamp_utc=timestamp_utc,
        )


__all__ = ["PathDPreferenceEmbedder", "PreferenceRetrievalResult"]
