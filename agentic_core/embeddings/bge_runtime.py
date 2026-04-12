"""Shared synchronous BGE-m3 runtime query embedder.

Single authoritative source for:
  - model name  (BGE_MODEL)
  - expected dim (BGE_QUERY_DIM)
  - lazy process-level singleton model load
  - one sync function: bge_embed_query(text) -> list[float]

Both SemanticRetriever (L1) and HybridSearchEngine (L3) import from here.
No async, no factory sovereignty path, no external network calls after first load.
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING

try:
    from sentence_transformers import SentenceTransformer

    _ST_AVAILABLE = True
except ImportError:
    SentenceTransformer = None  # type: ignore[assignment,misc]
    _ST_AVAILABLE = False

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer as _ST

logger = logging.getLogger(__name__)


class BGEInstallError(RuntimeError):
    """sentence-transformers package is not installed."""


# ── Constants ──────────────────────────────────────────────────────────────
BGE_MODEL: str = "BAAI/bge-m3"
BGE_QUERY_DIM: int = 1024

# ── Process-level singleton ────────────────────────────────────────────────
_model_lock = threading.Lock()
_bge_model: "_ST | None" = None


def _get_model() -> "_ST":
    """Return the process-level BGE-m3 model, loading it once on first call."""
    global _bge_model
    if _bge_model is None:
        with _model_lock:
            if _bge_model is None:
                if SentenceTransformer is None:
                    raise BGEInstallError(
                        "sentence-transformers is not installed. Run: pip install sentence-transformers"
                    )
                logger.info("Loading BGE model: %s", BGE_MODEL)
                _bge_model = SentenceTransformer(BGE_MODEL)
                logger.info("BGE model loaded: %s (dim=%d)", BGE_MODEL, BGE_QUERY_DIM)
    return _bge_model


def bge_embed_query(text: str) -> list[float]:
    """Return a 1024-dim L2-normalised BGE-m3 embedding for *text*.

    Args:
        text: Raw query string.

    Returns:
        List of 1024 floats, L2-normalised.

    Raises:
        RuntimeError: If sentence-transformers is not installed.
        RuntimeError: If the model returns an unexpected dimension
                      (BGE_DIM_MISMATCH — loud, never silent).
    """
    model = _get_model()
    vec: list[float] = model.encode(
        [text],
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    ).tolist()[0]

    if len(vec) != BGE_QUERY_DIM:
        raise RuntimeError(
            f"BGE_DIM_MISMATCH: query embedding has dim={len(vec)}, "
            f"expected {BGE_QUERY_DIM}. Model='{BGE_MODEL}' may have changed."
        )

    return [float(v) for v in vec]


def reset_model_for_testing() -> None:
    """Reset the singleton — test-only helper, never call in production."""
    global _bge_model
    with _model_lock:
        _bge_model = None
