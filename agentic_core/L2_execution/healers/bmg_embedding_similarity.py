"""
BMG Embedding Similarity — GPU-accelerated cosine similarity via BAAI/bge-m3.

Provides a single public function `bmg_cosine_similarity` that returns the
maximum cosine similarity between an unknown string and a list of candidate
strings using the BAAI/bge-m3 sentence embedding model.

Design invariants:
- Model is loaded lazily and cached as a module-level singleton.
- Requires sentence-transformers >= 2.6 and torch with CUDA support.
- Raises ImportError (not silently) if dependencies are missing — callers
  must catch and fall back to Jaccard.
- No global mutable state beyond the module-level model cache.
- All computation is float32; no half-precision accumulator drift.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

_MODEL_CACHE: object | None = None  # SentenceTransformer instance
_MODEL_ID = "BAAI/bge-m3"


def _get_model() -> object:
    """Load and cache the BGE-M3 model.  Raises ImportError if unavailable."""
    global _MODEL_CACHE  # noqa: PLW0603
    if _MODEL_CACHE is not None:
        return _MODEL_CACHE

    try:
        from sentence_transformers import SentenceTransformer  # type: ignore[import-untyped]
    except ImportError as exc:
        raise ImportError(
            "sentence-transformers is required for BMG embedding similarity. "
            "Install with: pip install sentence-transformers"
        ) from exc

    import torch

    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"[BMG] Loading {_MODEL_ID} on {device}")
    _MODEL_CACHE = SentenceTransformer(_MODEL_ID, device=device)
    logger.info(f"[BMG] Model loaded successfully on {device}")
    return _MODEL_CACHE


def bmg_cosine_similarity(unknown: str, candidates: list[str]) -> float:
    """Return the maximum cosine similarity between *unknown* and *candidates*.

    Args:
        unknown: The query string (e.g. a file path or violation description).
        candidates: Non-empty list of reference strings.

    Returns:
        Float in [0.0, 1.0] — maximum cosine similarity across all candidates.

    Raises:
        ImportError: If sentence-transformers or torch is not installed.
        ValueError: If candidates is empty.
    """
    if not candidates:
        raise ValueError("candidates must be non-empty")

    model = _get_model()

    import torch

    all_strings = [unknown] + candidates
    embeddings = model.encode(  # type: ignore[attr-defined]
        all_strings,
        convert_to_tensor=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    query_vec = embeddings[0]
    candidate_vecs = embeddings[1:]

    # Cosine similarity = dot product when vectors are L2-normalised
    similarities = torch.matmul(candidate_vecs, query_vec)
    max_sim: float = float(similarities.max().item())
    return max(0.0, min(1.0, max_sim))


def clear_model_cache() -> None:
    """Invalidate the cached model (for tests and hot-reload)."""
    global _MODEL_CACHE  # noqa: PLW0603
    _MODEL_CACHE = None


__all__ = [
    "bmg_cosine_similarity",
    "clear_model_cache",
]
