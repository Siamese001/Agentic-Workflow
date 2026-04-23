"""Embedding-based exemplar retrieval \u2014 W7 RH7.1.

Dynamic task-similarity selection via pluggable embedding provider. Complements
the static keyword-matching retriever in ``retriever.py`` from W4 \u2014 callers
choose per invocation.

Design
------
- ``EmbeddingProvider`` is a ``Protocol``. Concrete providers live elsewhere
  (vector_db MCP wrapper, local sentence-transformers, etc.) and are
  injected at call time. This keeps L4 free of provider-specific imports.
- Cosine similarity over unit-normalized vectors.
- Deterministic tie-break by ``exemplar_id`` ascending (mirrors static path).
- If the provider returns a zero-length vector for any input, that record is
  skipped (score 0) rather than causing a division-by-zero.
- Static fallback: ``select_with_fallback()`` uses embeddings if the
  provider is given, else delegates to the W4 Jaccard retriever.

Non-goal
--------
- No vector caching here. Providers are responsible for their own caching.
- No network calls in this module \u2014 pure math + iteration.
"""

from __future__ import annotations

import math
from typing import Protocol, Sequence

from agentic_core.L4_state.exemplars.bank import ExemplarBank, ExemplarRecord
from agentic_core.L4_state.exemplars.retriever import select_top_k as _static_select


class EmbeddingProvider(Protocol):
    """Injected embedding source.

    Implementations must return a vector of floats per input text, in the
    same order as the input. Empty input yields an empty vector.
    """

    name: str

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        ...


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = 0.0
    norm_a = 0.0
    norm_b = 0.0
    for av, bv in zip(a, b, strict=True):
        dot += av * bv
        norm_a += av * av
        norm_b += bv * bv
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (math.sqrt(norm_a) * math.sqrt(norm_b))


def _record_text(record: ExemplarRecord) -> str:
    """Compose the string the provider embeds for a record.

    Tags + input_text gives better signal than input_text alone because the
    curator's tag choice is often the cleanest task label.
    """
    tag_str = " ".join(record.tags)
    return f"{tag_str} {record.input_text}".strip()


def select_top_k_by_embedding(
    *,
    query: str,
    task_class: str,
    bank: ExemplarBank,
    provider: EmbeddingProvider,
    k: int = 3,
) -> tuple[ExemplarRecord, ...]:
    """Return top-k records by embedding cosine similarity.

    Args
    ----
    query:
        Free-form query to embed.
    task_class:
        Only records in this class are considered.
    bank:
        Exemplar store (from ``agentic_core.L4_state.exemplars.bank``).
    provider:
        Embedding source implementing ``EmbeddingProvider``.
    k:
        Max results. ``k <= 0`` returns ``()``.
    """
    if k <= 0:
        return ()
    candidates = bank.by_class(task_class)
    if not candidates:
        return ()

    texts = [query] + [_record_text(rec) for rec in candidates]
    vectors = provider.embed(texts)
    if len(vectors) != len(texts):
        raise ValueError(
            f"EmbeddingProvider {provider.name!r} returned {len(vectors)} "
            f"vectors for {len(texts)} inputs"
        )

    query_vec = vectors[0]
    scored = [
        (_cosine(query_vec, vectors[idx + 1]), rec.exemplar_id, rec)
        for idx, rec in enumerate(candidates)
    ]
    # Primary: -score (descending). Secondary: exemplar_id (ascending).
    scored.sort(key=lambda triple: (-triple[0], triple[1]))
    return tuple(rec for _, _, rec in scored[:k])


def select_with_fallback(
    *,
    query: str,
    task_class: str,
    bank: ExemplarBank,
    provider: EmbeddingProvider | None = None,
    k: int = 3,
) -> tuple[ExemplarRecord, ...]:
    """Use embedding retrieval if ``provider`` is given, else static Jaccard.

    Convenience for call sites that don't want to branch on provider
    availability themselves.
    """
    if provider is None:
        return _static_select(query=query, task_class=task_class, bank=bank, k=k)
    return select_top_k_by_embedding(
        query=query, task_class=task_class, bank=bank, provider=provider, k=k
    )


__all__ = [
    "EmbeddingProvider",
    "select_top_k_by_embedding",
    "select_with_fallback",
]
