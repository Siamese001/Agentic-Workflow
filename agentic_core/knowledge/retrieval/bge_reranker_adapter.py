"""BGE Reranker v2-m3 adapter - sentence-transformers CrossEncoder wrapper.

Per Author-Gate decision 2026-04-24 (DECISION_CAPTURED type=architecture_choice,
selected=bge-reranker-v2-m3, confidence=0.78). Thin adapter over
``sentence_transformers.CrossEncoder`` for ``BAAI/bge-reranker-v2-m3`` with
a module-level lazy singleton so the ~6-10s GPU warmup is paid once per
process and subsequent calls amortize to ~10-80ms per candidate batch.

Model sizing: 568M params, 1024-token ctx, multilingual, Apache-2.0.
Loads in FP16 (~1.3GB VRAM) on a 32GB GPU.

Failure modes: torch / sentence-transformers missing -> CrossEncoderUnavailable
(caller falls back to heuristic). GPU OOM -> caller catches and shrinks
batch_size or falls back.
"""

from __future__ import annotations

from agentic_core.config.model_catalog import (
    BGE_RERANKER_MODEL_ID,
)

import logging
import os
import threading
from typing import Any

logger = logging.getLogger(__name__)


class CrossEncoderUnavailable(RuntimeError):
    """torch + sentence-transformers required; at least one is missing."""


BGE_RERANKER_MODEL: str = BGE_RERANKER_MODEL_ID
BGE_RERANKER_MAX_LENGTH: int = 512
BGE_RERANKER_ALLOW_DOWNLOAD: bool = os.environ.get("BGE_RERANKER_ALLOW_DOWNLOAD", "false").lower() == "true"


_MODEL_LOCK = threading.Lock()
_MODEL: Any = None


def _resolve_device() -> str:
    """Co-locate reranker on the same device as the embedder."""
    try:
        from agentic_core.embeddings.bge_runtime import _resolve_device as _rd  # noqa: PLC0415

        return _rd()
    except ImportError:
        return "cpu"


def _load_model() -> Any:
    """Lazy process-level singleton load of the CrossEncoder.

    Raises CrossEncoderUnavailable if dependencies missing; caller is
    expected to catch this and fall back cleanly.
    """
    global _MODEL
    if _MODEL is not None:
        return _MODEL
    with _MODEL_LOCK:
        if _MODEL is not None:
            return _MODEL
        try:
            from sentence_transformers import CrossEncoder  # noqa: PLC0415
        except ImportError as exc:
            raise CrossEncoderUnavailable(f"sentence-transformers required for BGE reranker: {exc}") from exc
        device = _resolve_device()
        logger.info(
            "Loading BGE reranker: %s (device=%s, allow_download=%s)",
            BGE_RERANKER_MODEL,
            device,
            BGE_RERANKER_ALLOW_DOWNLOAD,
        )
        _MODEL = CrossEncoder(
            BGE_RERANKER_MODEL,
            max_length=BGE_RERANKER_MAX_LENGTH,
            device=device,
            local_files_only=not BGE_RERANKER_ALLOW_DOWNLOAD,
            trust_remote_code=False,
        )
        logger.info("BGE reranker loaded.")
        return _MODEL


def reset_for_testing() -> None:
    """Clear the singleton - test-only."""
    global _MODEL
    with _MODEL_LOCK:
        _MODEL = None


class BgeRerankerAdapter:
    """Thin, testable contract over the CrossEncoder.

    Usage:
        adapter = BgeRerankerAdapter()
        scores = adapter.score(query, [c.content for c in candidates])
        # scores[i] is a relevance score in R (sigmoided by the model head).
        # Higher = more relevant. Not bounded to [0, 1].
    """

    def __init__(self, *, batch_size: int = 32) -> None:
        self.batch_size = batch_size

    def score(self, query: str, candidate_texts: list[str]) -> list[float]:
        """Score each (query, candidate_text) pair.

        Returns a list of floats with len == len(candidate_texts). The order
        matches the input order; caller sorts by score to rerank.

        Raises:
            CrossEncoderUnavailable: deps missing.
            ValueError: empty query or empty candidates.
        """
        if not query or not query.strip():
            raise ValueError("query must be a non-empty string")
        if not candidate_texts:
            raise ValueError("candidate_texts must be non-empty")

        model = _load_model()
        pairs = [[query, text] for text in candidate_texts]
        raw = model.predict(
            pairs,
            batch_size=self.batch_size,
            show_progress_bar=False,
        )
        # CrossEncoder.predict may return numpy array, list, or torch tensor
        # depending on the ST version; normalize to a plain list of floats.
        if hasattr(raw, "tolist"):
            raw = raw.tolist()
        return [float(v) for v in raw]


__all__ = [
    "BGE_RERANKER_MODEL",
    "BGE_RERANKER_MAX_LENGTH",
    "BgeRerankerAdapter",
    "CrossEncoderUnavailable",
    "reset_for_testing",
]
