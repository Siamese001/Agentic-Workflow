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
import os
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
BGE_ALLOW_MODEL_DOWNLOAD: bool = os.environ.get("BGE_ALLOW_MODEL_DOWNLOAD", "false").lower() == "true"


def _resolve_device() -> str:
    """Pick the inference device for BGE-M3.

    Priority:
      1. Explicit EMBEDDING_DEVICE env var if set to cpu/cuda/mps
      2. CUDA if torch reports it available
      3. CPU fallback
    """
    override = os.environ.get("EMBEDDING_DEVICE", "").strip().lower()
    if override in {"cpu", "cuda", "mps"}:
        return override
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
    except (
        ImportError,
        RuntimeError,
    ):  # guardian: allow-silent-swallow -- torch is an optional dep; CPU fallback is the intended behavior when CUDA/torch is unavailable
        pass
    return "cpu"


# ── Process-level singleton ────────────────────────────────────────────────
_model_lock = threading.Lock()
_bge_model: "_ST | None" = None


def _sanitize_text(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    text = text.strip()
    if not text:
        raise ValueError("text must not be empty")
    return text


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
                device = _resolve_device()
                logger.info("Loading BGE model: %s (device=%s)", BGE_MODEL, device)
                _bge_model = SentenceTransformer(
                    BGE_MODEL,
                    device=device,
                    local_files_only=not BGE_ALLOW_MODEL_DOWNLOAD,
                    trust_remote_code=False,
                )
                logger.info("BGE model loaded: %s (dim=%d, device=%s)", BGE_MODEL, BGE_QUERY_DIM, device)
    return _bge_model


def bge_embed_batch(texts: list[str], batch_size: int = 64) -> list[list[float]]:
    """Embed a batch of texts in one model call for GPU throughput.

    This avoids the per-text Python loop overhead that forces single-item
    encodes when callers have many texts to embed (e.g. ChromaDB ingestion).

    Args:
        texts: List of strings to embed. Must all be non-empty after strip().
        batch_size: Max number of texts per internal .encode() call.

    Returns:
        List of 1024-dim L2-normalised embeddings, one per input text.
    """
    if not texts:
        return []
    sanitized = [_sanitize_text(t) for t in texts]
    model = _get_model()
    encoded = model.encode(
        sanitized,
        batch_size=batch_size,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    if encoded is None or len(encoded) != len(sanitized):
        raise RuntimeError(
            f"BGE_EMBED_FAILED: expected {len(sanitized)} rows, got {0 if encoded is None else len(encoded)}"
        )
    if encoded.shape[1] != BGE_QUERY_DIM:
        raise RuntimeError(f"BGE_DIM_MISMATCH: expected {BGE_QUERY_DIM}, got {encoded.shape[1]}")
    return encoded.tolist()


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
    sanitized = _sanitize_text(text)
    model = _get_model()
    encoded = model.encode(
        [sanitized],
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    if encoded is None or len(encoded) != 1:
        raise RuntimeError("BGE_EMBED_FAILED: expected a single embedding row")
    vec: list[float] = encoded.tolist()[0]
    if not isinstance(vec, list):
        raise RuntimeError("BGE_EMBED_FAILED: model returned a non-list embedding payload")

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


# ── W5.3: opt-in multi-vector path (dense + sparse + ColBERT) ──────────────
#
# BGE-M3 is a true multi-vector model. Beyond the 1024-dim dense vector
# every ``bge_embed_query`` / ``bge_embed_batch`` call already returns, the
# same forward pass yields:
#
#   - lexical_weights: dict[token_id, weight]  — BM25-like sparse vector
#   - colbert_vecs: list[list[float]]          — per-token fine-grained vec
#
# These are accessible only via ``FlagEmbedding.BGEM3FlagModel``, NOT via
# the generic ``SentenceTransformer`` wrapper used above. So the multi-vec
# path carries its own optional singleton and fails loudly if the dependency
# is not installed. Default pipeline behaviour (dense only) is unchanged;
# opt-in callers flip on via ``BGE_MULTIVEC_ENABLED=true`` and consume the
# returned dict.

_multivec_lock = threading.Lock()
_multivec_model: object | None = None


class BGEMultiVecUnavailable(RuntimeError):
    """FlagEmbedding is not installed or BGE-M3 multi-vec is disabled."""


def _get_multivec_model() -> object:
    """Return the FlagEmbedding BGEM3FlagModel singleton.

    Loaded lazily on first call. Respects the same ``BGE_ALLOW_MODEL_DOWNLOAD``
    switch as the dense singleton.
    """
    global _multivec_model
    if _multivec_model is None:
        with _multivec_lock:
            if _multivec_model is None:
                try:
                    from FlagEmbedding import BGEM3FlagModel  # type: ignore[import-not-found]
                except ImportError as exc:
                    raise BGEMultiVecUnavailable(
                        "FlagEmbedding is not installed. Run: pip install -U FlagEmbedding"
                    ) from exc
                device = _resolve_device()
                use_fp16 = device == "cuda"
                logger.info(
                    "Loading BGE-M3 multi-vec model: %s (device=%s, fp16=%s)",
                    BGE_MODEL,
                    device,
                    use_fp16,
                )
                _multivec_model = BGEM3FlagModel(
                    BGE_MODEL,
                    use_fp16=use_fp16,
                )
    return _multivec_model


def bge_embed_multi(
    texts: list[str],
    *,
    batch_size: int = 32,
    return_dense: bool = True,
    return_sparse: bool = True,
    return_colbert: bool = True,
) -> dict[str, object]:
    """Embed ``texts`` and return any subset of dense / sparse / ColBERT vectors.

    Args:
        texts: Non-empty list of non-empty strings.
        batch_size: Forwarded to the FlagEmbedding encoder.
        return_dense: Include the 1024-dim dense vectors.
        return_sparse: Include the sparse lexical_weights dict per text.
        return_colbert: Include the ColBERT per-token vectors.

    Returns:
        Dict with whichever of ``{"dense": list[list[float]],
        "sparse": list[dict[int, float]], "colbert": list[list[list[float]]]}``
        were requested.

    Raises:
        BGEMultiVecUnavailable: FlagEmbedding not installed.
        ValueError: Inputs empty or malformed.
    """
    if not texts:
        return {}
    sanitized = [_sanitize_text(t) for t in texts]
    model = _get_multivec_model()
    result = model.encode(  # type: ignore[attr-defined]
        sanitized,
        batch_size=batch_size,
        return_dense=return_dense,
        return_sparse=return_sparse,
        return_colbert_vecs=return_colbert,
    )

    out: dict[str, object] = {}
    if return_dense:
        dense = result.get("dense_vecs")
        if dense is None:
            raise RuntimeError("BGE_MULTIVEC_FAILED: dense_vecs missing from FlagEmbedding output")
        out["dense"] = dense.tolist() if hasattr(dense, "tolist") else list(dense)
    if return_sparse:
        sparse = result.get("lexical_weights")
        if sparse is None:
            raise RuntimeError("BGE_MULTIVEC_FAILED: lexical_weights missing")
        # Convert numpy keys/values to plain python ints/floats for JSON safety
        out["sparse"] = [{int(k): float(v) for k, v in weights.items()} for weights in sparse]
    if return_colbert:
        colbert = result.get("colbert_vecs")
        if colbert is None:
            raise RuntimeError("BGE_MULTIVEC_FAILED: colbert_vecs missing")
        out["colbert"] = [vec.tolist() if hasattr(vec, "tolist") else list(vec) for vec in colbert]
    return out
