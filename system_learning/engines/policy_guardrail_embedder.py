"""PolicyGuardrailEmbedder — Semantic memory for guardrail drift cases.

Converts PolicyGuardrailCase objects into CorpusRecords for seed-pack
ingestion and provides nearest-neighbour retrieval over historical
guardrail blocks, false-positives, and false-negatives.

Enables:
  - Calibrating strictness by retrieving similar past blocks
  - Identifying drift: "what changed behavior after this policy root?"
  - False-positive/negative pattern recognition
  - Policy-hash neighborhood search: incidents linked to a policy change

Design constraints:
- No wall-clock reads; all timestamps provided by caller.
- Deterministic text serialization via PolicyGuardrailCase.to_embedding_text().
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
from system_learning.types.semantic_memory_types import PolicyGuardrailCase

logger = logging.getLogger(__name__)

_NAMESPACE = "policy_guardrail_cases"


@dataclass(frozen=True)
class GuardrailRetrievalResult:
    """Nearest-neighbour result from policy guardrail case retrieval.

    C0_INFORMATIONAL only — no routing influence.
    """

    content_hash: str
    similarity_score: float
    case_id: str
    policy_hash: str
    verdict: str
    strictness_level: str
    content_preview: str


class PolicyGuardrailEmbedder:
    """Converts PolicyGuardrailCase objects to corpus records and retrieves similar cases.

    Usage:
        embedder = PolicyGuardrailEmbedder()
        embedder.ingest(case)
        similar = embedder.retrieve_for_policy_hash(policy_hash, k=5)
    """

    def __init__(self, max_buffer: int = DEFAULT_EMBEDDER_BUFFER_SIZE) -> None:
        if max_buffer < 1:
            raise ValueError(f"max_buffer must be >= 1, got {max_buffer}")
        self._max_buffer = max_buffer
        self._lock = threading.Lock()
        self._records: list[CorpusRecord] = []
        self._meta: dict[str, dict[str, Any]] = {}

    def ingest(self, case: PolicyGuardrailCase) -> CorpusRecord:
        """Convert a PolicyGuardrailCase to a CorpusRecord and buffer it.

        Args:
            case: The guardrail case to ingest.

        Returns:
            The generated CorpusRecord.
        """
        text = case.to_embedding_text()
        content_hash = compute_content_hash(text.encode("utf-8"))
        corpus_record = CorpusRecord(
            text=text,
            trace_id=case.trace_id,
            content_hash=content_hash,
            namespace=_NAMESPACE,
        )
        meta = {
            "case_id": case.case_id,
            "policy_hash": case.policy_hash,
            "policy_root": case.policy_root,
            "verdict": case.verdict,
            "strictness_level": case.strictness_level,
            "case_hash": case.case_hash,
        }
        with self._lock:
            if len(self._records) >= self._max_buffer:
                dropped = self._records.pop(0)
                self._meta.pop(dropped.content_hash, None)
                logger.debug("PolicyGuardrailEmbedder: buffer full, dropped oldest record")
            self._records.append(corpus_record)
            self._meta[content_hash] = meta
        return corpus_record

    def ingest_batch(self, cases: list[PolicyGuardrailCase]) -> list[CorpusRecord]:
        """Ingest multiple PolicyGuardrailCases.

        Args:
            cases: List of guardrail cases.

        Returns:
            List of generated CorpusRecords in the same order.
        """
        return [self.ingest(c) for c in cases]

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

    def retrieve_for_payload(
        self,
        payload_summary: str,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[GuardrailRetrievalResult]:
        """Retrieve cases similar to a new blocked payload.

        Primary use: when L5 blocks a payload, retrieve semantically similar
        past decisions to calibrate whether the block is likely a true positive.

        Args:
            payload_summary: Summary of the blocked payload.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of GuardrailRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(payload_summary, k=k, namespace=namespace)

    def retrieve_for_policy_hash(
        self,
        policy_hash: str,
        *,
        k: int = 10,
        namespace: str = _NAMESPACE,
    ) -> list[GuardrailRetrievalResult]:
        """Retrieve incidents linked to a policy hash neighborhood.

        Use when a policy changes to find all historical incidents that were
        governed by this or similar policy roots — answers "what changed
        behavior after this policy root?".

        Args:
            policy_hash: The policy hash to anchor the neighborhood search.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of GuardrailRetrievalResult — C0_INFORMATIONAL.
        """
        query_text = f"policy:{policy_hash}"
        return self._retrieve(query_text, k=k, namespace=namespace)

    def retrieve_similar(
        self,
        query_case: PolicyGuardrailCase,
        *,
        k: int = 5,
        namespace: str = _NAMESPACE,
    ) -> list[GuardrailRetrievalResult]:
        """Retrieve nearest-neighbour guardrail cases via sovereign semantic cache.

        Args:
            query_case: The case to find neighbours for.
            k: Maximum results.
            namespace: Seed pack namespace.

        Returns:
            List of GuardrailRetrievalResult — C0_INFORMATIONAL.
        """
        return self._retrieve(query_case.to_embedding_text(), k=k, namespace=namespace)

    def _retrieve(
        self,
        query_text: str,
        *,
        k: int,
        namespace: str,
    ) -> list[GuardrailRetrievalResult]:
        k = min(k, 20)
        try:
            from agentic_core.interfaces.embeddings import query_similarity

            raw_results = query_similarity(query_text, top_k=k, namespace=namespace)
            out: list[GuardrailRetrievalResult] = []
            for r in raw_results:
                ch = r.content_hash
                meta = self._meta.get(ch, {})
                out.append(
                    GuardrailRetrievalResult(
                        content_hash=ch,
                        similarity_score=r.similarity_score,
                        case_id=meta.get("case_id", ""),
                        policy_hash=meta.get("policy_hash", ""),
                        verdict=meta.get("verdict", ""),
                        strictness_level=meta.get("strictness_level", ""),
                        content_preview=r.content_preview,
                    )
                )
            return out
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.debug("PolicyGuardrailEmbedder._retrieve: %s", exc)
            return []

    @staticmethod
    def case_from_l5_block(
        *,
        case_id: str,
        blocked_payload_summary: str,
        remediation_text: str,
        policy_hash: str,
        policy_root: str,
        verdict: str,
        strictness_level: str,
        trace_id: str,
        timestamp_utc: int,
    ) -> PolicyGuardrailCase:
        """Convenience constructor that validates verdict literal."""
        if verdict not in ("true_positive", "false_positive", "false_negative"):
            raise ValueError(f"verdict must be true_positive/false_positive/false_negative, got {verdict!r}")
        return PolicyGuardrailCase(
            case_id=case_id,
            blocked_payload_summary=blocked_payload_summary,
            remediation_text=remediation_text,
            policy_hash=policy_hash,
            policy_root=policy_root,
            verdict=verdict,  # type: ignore[arg-type]
            strictness_level=strictness_level,
            trace_id=trace_id,
            timestamp_utc=timestamp_utc,
        )


__all__ = ["PolicyGuardrailEmbedder", "GuardrailRetrievalResult"]
