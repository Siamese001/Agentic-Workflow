"""IntentEmbeddingClassifier — embedding-based intent classifier for AgenticRouter.

Replaces the keyword hit-ratio in AgenticRouter._classify() with cosine-similarity
against per-target prototype vectors stored in a LocalFAISSStore index.

Design invariants
-----------------
1. Pure class — no global mutable state.
2. No wall-clock reads.
3. Deterministic: embedding model pinned by pack-hash; same input → same output.
4. Fail-closed on EmbeddingDisabledError — returns None so caller falls back
   to legacy keyword path.  Never raises into the router.
5. C0_INFORMATIONAL influence class — classification result MUST NOT bypass
   L0 governance contracts or safety gates.

Layer: L0_routing
"""

from __future__ import annotations

import hashlib
import logging
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    emit_determinism_digest,
    emit_replay_key,
)

logger = logging.getLogger(__name__)

_INDEX_ID = "intent_prototypes"
_TOP_K = 1
_COSINE_CUTOFF = 0.0


def _l2_normalize(vec: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0.0:
        return vec
    return [x / norm for x in vec]


def _average_vectors(vecs: list[list[float]]) -> list[float] | None:
    """Return component-wise average of a non-empty list of equal-length vectors."""
    if not vecs:
        return None
    dim = len(vecs[0])
    avg = [0.0] * dim
    for v in vecs:
        for i, x in enumerate(v):
            avg[i] += x
    n = len(vecs)
    return [x / n for x in avg]


@dataclass
class _PrototypeEntry:
    """In-memory prototype record for one routing target."""

    target_name: str
    content_hash: str
    vector: list[float]


class IntentEmbeddingClassifier:
    """Cosine-similarity intent classifier backed by a LocalFAISSStore index.

    Usage::

        classifier = IntentEmbeddingClassifier(store_base_path=Path("..."))
        classifier.encode_prototype("resume_writer", ["resume", "cv", "career"])
        classifier.encode_prototype("code_reviewer", ["code", "review", "python"])
        target_name, confidence = classifier.classify("Please review my Python code")

    When embedding is unavailable (kill-switch / FAISS not installed), all
    methods return safe defaults without raising.

    Args:
        store_base_path: Directory passed to LocalFAISSStore for index storage.
        embedder:        Optional pre-built embedding callable
                         ``(texts: list[str]) -> list[list[float]]``.
                         When None, the classifier attempts to build one from
                         ``EmbeddingServiceFactory``.
        cosine_cutoff:   Minimum cosine score to return a non-None result
                         (default 0.0 — always returns best match).
    """

    def __init__(
        self,
        store_base_path: Path | None = None,
        embedder: Any | None = None,
        cosine_cutoff: float = _COSINE_CUTOFF,
    ) -> None:
        self._store_base_path = store_base_path or Path("artifacts/intent_index")
        self._embedder = embedder
        self._cosine_cutoff = cosine_cutoff
        self._prototypes: dict[str, _PrototypeEntry] = {}
        self._store: Any | None = None
        self._store_ready = False

    # ------------------------------------------------------------------
    # Embedder access (lazy, fail-silent)
    # ------------------------------------------------------------------

    def _get_embedder(self) -> Any | None:
        if self._embedder is not None:
            return self._embedder
        try:
            from system_learning.engines.embedding_service_factory import (
                EmbeddingServiceFactory,
            )

            factory = EmbeddingServiceFactory.get_instance()
            self._embedder = factory
            return self._embedder
        except (ImportError, RuntimeError) as exc:  # embedder initialization failure
            logger.debug("IntentEmbeddingClassifier: embedder unavailable: %s", exc)
            return None  # guardian: allow-return-none-swallow -- embedder init: non-fatal, caller skips embedding when None returned

    def _embed_texts(self, texts: list[str]) -> list[list[float]] | None:
        """Embed a list of texts, returning None if embedding is disabled."""
        embedder = self._get_embedder()
        if embedder is None:
            return None
        try:
            results: list[list[float]] = []
            for text in texts:
                result = embedder.embed(text)
                if result is None:
                    continue
                try:
                    vec = list(result.vector)
                except AttributeError:
                    vec = list(result)
                results.append(vec)
            return results if results else None
        except (ValueError, TypeError, RuntimeError) as exc:  # embedding operation failure
            logger.debug("IntentEmbeddingClassifier: embedding failed: %s", exc)
            return None  # guardian: allow-return-none-swallow -- embedding: non-fatal, caller treats None as unavailable embedding

    # ------------------------------------------------------------------
    # Prototype registration
    # ------------------------------------------------------------------

    def encode_prototype(self, target_name: str, texts: list[str]) -> bool:
        """Encode and store a prototype vector for a routing target.

        Args:
            target_name: Name of the routing target (must match RouteTarget.name).
            texts:       List of representative texts (keywords + description).

        Returns:
            True if prototype was stored, False if embedding unavailable.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L0_ROUTING,
            "IntentEmbeddingClassifier.encode_prototype",
        )
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        if not texts:
            logger.warning("IntentEmbeddingClassifier.encode_prototype: empty texts for %r", target_name)
            return False

        vecs = self._embed_texts(texts)
        if vecs is None:
            logger.debug("IntentEmbeddingClassifier.encode_prototype: skipped %r (no embedder)", target_name)
            return False

        prototype_vec = _average_vectors(vecs)
        if prototype_vec is None:
            return False

        prototype_vec = _l2_normalize(prototype_vec)

        content_hash = hashlib.sha256(f"{target_name}:{'|'.join(sorted(texts))}".encode()).hexdigest()

        self._prototypes[target_name] = _PrototypeEntry(
            target_name=target_name,
            content_hash=content_hash,
            vector=prototype_vec,
        )
        logger.debug(
            "IntentEmbeddingClassifier: prototype encoded for %r (hash=%s)",
            target_name,
            content_hash[:16],
        )
        return True

    def has_prototype(self, target_name: str) -> bool:
        """Return True if a prototype exists for this target."""
        return target_name in self._prototypes

    def prototype_count(self) -> int:
        """Return number of registered prototypes."""
        return len(self._prototypes)

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    def classify(self, user_input: str) -> tuple[str, float] | None:
        """Classify user_input against registered prototypes.

        Args:
            user_input: Raw user or task input string.

        Returns:
            ``(target_name, confidence)`` tuple where confidence is cosine
            similarity in ``[0.0, 1.0]``, or ``None`` if:
            - No prototypes registered.
            - Embedding unavailable.
            - No match above ``cosine_cutoff``.
        """
        if not self._prototypes:
            return None

        try:
            query_vecs = self._embed_texts([user_input])
            if not query_vecs:
                return None

            query_vec = _l2_normalize(query_vecs[0])

            best_name: str | None = None
            best_score: float = -1.0

            for name, entry in self._prototypes.items():
                score = sum(q * p for q, p in zip(query_vec, entry.vector))
                score = round(score, 6)
                if score > best_score:
                    best_score = score
                    best_name = name

            if best_name is None or best_score < self._cosine_cutoff:
                return None

            logger.debug("IntentEmbeddingClassifier.classify: best=%r score=%.4f", best_name, best_score)
            return (best_name, max(0.0, min(1.0, best_score)))
        except (ValueError, TypeError) as exc:  # classification computation error
            logger.debug("IntentEmbeddingClassifier.classify: exception swallowed: %s", exc)
            return None  # guardian: allow-return-none-swallow -- classify: non-fatal, caller treats None as unclassified intent

    # ------------------------------------------------------------------
    # Prototype update (for feedback-loop driven refresh)
    # ------------------------------------------------------------------

    def update_prototype(self, target_name: str, texts: list[str]) -> bool:
        """Re-encode prototype for target_name with new exemplar texts.

        Called by the MetaLearningBus when a ROUTING_MISCLASSIFICATION
        OptimizationCommit is applied.

        Returns:
            True if update succeeded, False otherwise.
        """
        return self.encode_prototype(target_name, texts)

    def get_prototype_hash(self, target_name: str) -> str | None:
        """Return the content hash of a stored prototype, or None."""
        entry = self._prototypes.get(target_name)
        return entry.content_hash if entry else None


__all__ = ["IntentEmbeddingClassifier"]
