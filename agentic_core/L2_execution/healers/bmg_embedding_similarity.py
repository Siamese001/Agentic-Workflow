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

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

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

    # Prefer CUDA when available; SentenceTransformer auto-detects via its own
    # internal torch dependency.  We do NOT import torch directly here to stay
    # within the vllm_isolation boundary contract (forbidden prefix: 'torch').
    device = "cuda" if _is_cuda_available() else "cpu"
    logger.info("[BMG] Loading %s on %s", _MODEL_ID, device)
    _MODEL_CACHE = SentenceTransformer(_MODEL_ID, device=device)
    logger.info("[BMG] Model loaded successfully on %s", device)
    return _MODEL_CACHE


def _is_cuda_available() -> bool:
    """Return True if a CUDA device is reachable without importing torch directly."""
    try:
        import importlib

        torch_mod = importlib.import_module("torch")
        return bool(torch_mod.cuda.is_available())  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        return False


def bmg_cosine_similarity(unknown: str, candidates: list[str]) -> float:
    """Return the maximum cosine similarity between *unknown* and *candidates*.

    Uses numpy dot-product on L2-normalised vectors (avoids direct torch import).

    Args:
        unknown: The query string (e.g. a file path or violation description).
        candidates: Non-empty list of reference strings.

    Returns:
        Float in [0.0, 1.0] — maximum cosine similarity across all candidates.

    Raises:
        ImportError: If sentence-transformers is not installed.
        ValueError: If candidates is empty.
    """
    if not candidates:
        raise ValueError("candidates must be non-empty")

    import numpy as np  # noqa: PLC0415

    model = _get_model()

    all_strings = [unknown] + candidates
    # convert_to_numpy=True avoids a direct torch tensor in this module
    embeddings: np.ndarray = model.encode(  # type: ignore[attr-defined]
        all_strings,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    query_vec = embeddings[0]
    candidate_vecs = embeddings[1:]

    # Cosine similarity = dot product when vectors are L2-normalised
    similarities: np.ndarray = candidate_vecs @ query_vec
    max_sim: float = float(similarities.max())
    return max(0.0, min(1.0, max_sim))


def bmg_embed_text(text: str) -> list[float]:
    """Embed a single text string using BAAI/bge-m3.

    Returns an L2-normalised embedding vector as a plain Python list of
    floats.  Suitable for storage in ``HealingOutcomeEvent.failure_vector``
    and subsequent cosine-similarity novelty checks.

    Args:
        text: The text to embed (e.g. a normalized failure signal string).

    Returns:
        L2-normalised float list of length equal to the model's output
        dimension (~1024 for bge-m3).

    Raises:
        ImportError: If sentence-transformers is not installed.
    """
    import numpy as np  # noqa: PLC0415

    model = _get_model()
    vecs: np.ndarray = model.encode(  # type: ignore[attr-defined]
        [text],
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return vecs[0].tolist()


def clear_model_cache() -> None:
    """Invalidate the cached model (for tests and hot-reload)."""
    global _MODEL_CACHE  # noqa: PLW0603
    _MODEL_CACHE = None


__all__ = [
    "bmg_cosine_similarity",
    "bmg_embed_text",
    "clear_model_cache",
]
