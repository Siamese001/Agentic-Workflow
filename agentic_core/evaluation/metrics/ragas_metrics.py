"""RAGAS-style evaluation metrics.

Deterministic, BGE-cosine-based implementations of the four core RAG quality
dimensions:

- FaithfulnessMetric:     answer attribution to retrieved context chunks
- AnswerRelevancyMetric:  query-answer cosine similarity
- ContextPrecisionMetric: fraction of retrieved chunks that are relevant
- GroundednessMetric:     per-claim attribution to context
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Any

from .base import EvaluationMetric

try:
    from agentic_core.runtime.contracts.lifecycle_trace_contract import (
        LayerSegment,
        _emit_records_execution_trace,
    )
except ModuleNotFoundError:

    class LayerSegment:
        L3_ORCHESTRATION = "L3_ORCHESTRATION"

    def _emit_records_execution_trace(*args: Any, **kwargs: Any) -> None:
        return None


def _trace_id(operation: str, payload: str) -> str:
    """Stable trace ID so metric execution remains replay-friendly."""
    return hashlib.sha256(f"{operation}|{payload}".encode("utf-8")).hexdigest()[:16]


_DEFAULT_EMBED_DIM = 1024
_FAITHFULNESS_THRESHOLD = 0.75


def _cosine(a: list[float], b: list[float]) -> float:
    """Deterministic cosine similarity; returns 0.0 on zero-norm vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum((x * y for x, y in zip(a, b)))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return max(-1.0, min(1.0, dot / (norm_a * norm_b)))


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences on .!? boundaries; strips empty results."""
    parts = re.split("(?<=[.!?])\\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _get_embedder():
    """Return a callable embed(text: str) -> list[float] using BGE-m3 or stub."""
    try:
        from agentic_core.L3_orchestration.healers.bmg_embedding_similarity import bmg_embed_text

        return bmg_embed_text
    except (ImportError, AttributeError, RuntimeError, ValueError):

        def _stub(text: str) -> list[float]:
            return [0.0] * _DEFAULT_EMBED_DIM

        return _stub


class FaithfulnessMetric(EvaluationMetric):
    """Measures what fraction of answer sentences are attributable to context.

    ``score = attributable_sentences / total_sentences``

    A sentence is attributable if its cosine similarity to any context chunk
    exceeds ``attribution_threshold`` (default 0.75).
    """

    def __init__(self, attribution_threshold: float = _FAITHFULNESS_THRESHOLD) -> None:
        self._threshold = attribution_threshold
        self._embed = _get_embedder()

    @property
    def name(self) -> str:
        return "faithfulness"

    def compute(self, prediction: str, ground_truth: Any = None, context: list[str] | None = None) -> float:
        trace_id = _trace_id(
            "FaithfulnessMetric.compute",
            f"{len(prediction)}|{len(context) if context else 0}|{self._threshold}",
        )
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "FaithfulnessMetric.compute",
        )

        if not prediction or not context:
            return 0.0
        sentences = _split_sentences(prediction)
        if not sentences:
            return 0.0
        context_embeddings = [self._embed(c) for c in context]
        attributable = 0
        for sentence in sentences:
            s_emb = self._embed(sentence)
            if any(_cosine(s_emb, c_emb) >= self._threshold for c_emb in context_embeddings):
                attributable += 1
        return round(attributable / len(sentences), 6)


class AnswerRelevancyMetric(EvaluationMetric):
    """Cosine similarity between query embedding and answer embedding.

    ``score = cosine(embed(query), embed(answer))``
    """

    def __init__(self) -> None:
        self._embed = _get_embedder()

    @property
    def name(self) -> str:
        return "answer_relevancy"

    def compute(self, prediction: str, ground_truth: str, context: Any = None) -> float:
        """
        Args:
            prediction: Generated answer.
            ground_truth: The query string (repurposed as query for relevancy scoring).
            context: Ignored.
        """
        trace_id = _trace_id(
            "AnswerRelevancyMetric.compute",
            f"{len(prediction)}|{len(ground_truth)}",
        )
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "AnswerRelevancyMetric.compute",
        )

        if not prediction or not ground_truth:
            return 0.0
        query_emb = self._embed(ground_truth)
        answer_emb = self._embed(prediction)
        return round(max(0.0, _cosine(query_emb, answer_emb)), 6)


class ContextPrecisionMetric(EvaluationMetric):
    """Set-based context precision.

    ``score = |relevant ∩ retrieved| / |retrieved|``

    Uses chunk IDs directly; no embedding required.
    """

    @property
    def name(self) -> str:
        return "context_precision"

    def compute(
        self,
        prediction: list[str],
        ground_truth: set[str] | list[str],
        context: Any = None,
    ) -> float:
        """
        Args:
            prediction: Retrieved chunk IDs.
            ground_truth: Ground-truth relevant chunk IDs.
            context: Ignored.
        """
        trace_id = _trace_id(
            "ContextPrecisionMetric.compute",
            f"{len(prediction)}|{len(ground_truth) if ground_truth else 0}",
        )
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "ContextPrecisionMetric.compute",
        )

        if not prediction:
            return 0.0
        retrieved = list(prediction)
        relevant = set(ground_truth) if ground_truth else set()
        hits = sum(1 for cid in retrieved if cid in relevant)
        return round(hits / len(retrieved), 6)


class GroundednessMetric(EvaluationMetric):
    """Per-claim attribution to context chunks.

    Each sentence in ``prediction`` is treated as a claim.
    ``score = attributable_claims / total_claims``.

    No context → groundedness = 0.0 (conservative).
    """

    def __init__(self, attribution_threshold: float = _FAITHFULNESS_THRESHOLD) -> None:
        self._threshold = attribution_threshold
        self._embed = _get_embedder()

    @property
    def name(self) -> str:
        return "groundedness"

    def compute(self, prediction: str, ground_truth: Any = None, context: list[str] | None = None) -> float:
        trace_id = _trace_id(
            "GroundednessMetric.compute",
            f"{len(prediction)}|{len(context) if context else 0}|{self._threshold}",
        )
        _emit_records_execution_trace(
            trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "GroundednessMetric.compute",
        )

        if not prediction or not context:
            return 0.0
        claims = _split_sentences(prediction)
        if not claims:
            return 0.0
        context_embeddings = [self._embed(c) for c in context]
        grounded = 0
        for claim in claims:
            c_emb = self._embed(claim)
            if any(_cosine(c_emb, ctx_emb) >= self._threshold for ctx_emb in context_embeddings):
                grounded += 1
        return round(grounded / len(claims), 6)


__all__ = [
    "FaithfulnessMetric",
    "AnswerRelevancyMetric",
    "ContextPrecisionMetric",
    "GroundednessMetric",
    "_cosine",
    "_split_sentences",
]
