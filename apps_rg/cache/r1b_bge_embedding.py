"""BGE-M3 embeddings for apps_rg R1B semantic cache (Chroma vector store only).

When ``resolve_apps_rg_embedding_settings().embedding_model_resolved`` is true, all
R1B intent/chunk vectors use explicit local BGE. Pseudo-digest vectors are fallback
only when embeddings are disabled (tests / CI without weights).
"""

from __future__ import annotations

import logging
import threading
from typing import Any

from agentic_core.config.model_catalog import BGE_M3_MODEL_ID

from apps_rg.cache.r1b_constants import R1B_STORAGE_SUBSYSTEM

_logger = logging.getLogger(__name__)

_BGE_DIM = 1024
_model_lock = threading.Lock()
_bge_model: Any = None


def bge_embeddings_active() -> bool:
    from apps_rg.runtime.embedding_settings import resolve_apps_rg_embedding_settings

    s = resolve_apps_rg_embedding_settings()
    return bool(s.embeddings_enabled and s.embedding_model_resolved)


def _get_bge_model() -> Any:
    global _bge_model
    if _bge_model is not None:
        return _bge_model
    with _model_lock:
        if _bge_model is not None:
            return _bge_model
        from apps_rg.runtime.embedding_settings import (
            load_bge_sentence_transformer,
            resolve_apps_rg_embedding_settings,
        )

        settings = resolve_apps_rg_embedding_settings()
        if not settings.embedding_model_resolved:
            return None
        try:
            _bge_model = load_bge_sentence_transformer(settings)
        except Exception as exc:  # guardian: allow-broad-exception -- P2 burndown: BGE optional when embeddings off-path  # guardian: allow-return-none-swallow -- P2 burndown: pseudo-digest fallback when load fails
            from apps_rg.runtime.embedding_settings import AppsRgEmbeddingFailClosedError
            from apps_rg.runtime.product_output_policy import require_live_bge_embeddings

            if require_live_bge_embeddings():
                raise AppsRgEmbeddingFailClosedError(
                    f"BGE-M3 load failed on product path: {exc}"
                ) from exc
            _logger.warning("R1B BGE load failed (%s); using pseudo-digest fallback", exc)
            return None
        return _bge_model


def reset_bge_model_for_testing() -> None:
    global _bge_model
    with _model_lock:
        _bge_model = None


def embed_text_bge(text: str) -> list[float] | None:
    """L2-normalized BGE-M3 embedding; None when BGE unavailable."""
    stripped = (text or "").strip()
    if not stripped:
        return None
    model = _get_bge_model()
    if model is None:
        return None
    encoded = model.encode(
        [stripped],
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    if encoded is None or len(encoded) != 1:
        return None
    vec = encoded.tolist()[0]
    if len(vec) != _BGE_DIM:
        raise RuntimeError(f"BGE_DIM_MISMATCH: got {len(vec)}, expected {_BGE_DIM}")
    return [float(v) for v in vec]


def intent_vector_payload(*, intent_text: str, digest: str) -> dict[str, Any]:
    """Canonical vector JSON persisted under ``vectors/<record_id>.json``."""
    from apps_rg.cache.r1b_intent_vector import normalized_intent_digest, pseudo_vector_from_digest

    from apps_rg.runtime.embedding_settings import AppsRgEmbeddingFailClosedError
    from apps_rg.runtime.product_output_policy import require_live_bge_embeddings

    digest = digest or normalized_intent_digest(intent_text)
    bge = embed_text_bge(intent_text)
    if bge is not None:
        return {
            "subsystem": R1B_STORAGE_SUBSYSTEM,
            "embedding_model": BGE_M3_MODEL_ID,
            "embedding_provider": "bge_local",
            "not_c0_fact_vectors": True,
            "not_chroma_default_ef": True,
            "normalized_intent_digest": digest,
            "dimensions": _BGE_DIM,
            "values": bge,
        }
    if require_live_bge_embeddings():
        raise AppsRgEmbeddingFailClosedError(
            "BGE-M3 embedding required; pseudo_digest_fallback forbidden on product path"
        )
    return {
        "subsystem": R1B_STORAGE_SUBSYSTEM,
        "embedding_model": "pseudo_digest_fallback",
        "not_c0_fact_vectors": True,
        "normalized_intent_digest": digest,
        "dimensions": 32,
        "values": pseudo_vector_from_digest(digest),
        "fallback_reason": "bge_unavailable",
    }


def chunk_vector_payload(*, chunk_text: str, chunk_id: str) -> dict[str, Any]:
    from apps_rg.runtime.embedding_settings import AppsRgEmbeddingFailClosedError
    from apps_rg.runtime.product_output_policy import require_live_bge_embeddings

    text = (chunk_text or chunk_id or "").strip()
    bge = embed_text_bge(text) if text else None
    if bge is not None:
        return {
            "chunk_id": chunk_id,
            "embedding_model": BGE_M3_MODEL_ID,
            "dimensions": _BGE_DIM,
            "values": bge,
        }
    if require_live_bge_embeddings():
        raise AppsRgEmbeddingFailClosedError(
            f"BGE-M3 chunk embedding required; pseudo_digest forbidden (chunk_id={chunk_id!r})"
        )
    from apps_rg.cache.r1b_intent_vector import normalized_intent_digest, pseudo_vector_from_digest

    digest = normalized_intent_digest(text or chunk_id)
    return {
        "chunk_id": chunk_id,
        "embedding_model": "pseudo_digest_fallback",
        "dimensions": 32,
        "values": pseudo_vector_from_digest(digest),
    }


def resolve_query_vector(intent_text: str, digest: str) -> tuple[list[float], str]:
    """Query vector for R1B lookup — BGE when active, else pseudo (tests only)."""
    from apps_rg.cache.r1b_intent_vector import pseudo_vector_from_digest
    from apps_rg.runtime.embedding_settings import AppsRgEmbeddingFailClosedError
    from apps_rg.runtime.product_output_policy import require_live_bge_embeddings

    bge = embed_text_bge(intent_text)
    if bge is not None:
        return bge, "bge_m3"
    if require_live_bge_embeddings():
        raise AppsRgEmbeddingFailClosedError(
            "BGE-M3 query vector required; pseudo_digest forbidden on product path"
        )
    return pseudo_vector_from_digest(digest), "pseudo_digest"


__all__ = [
    "bge_embeddings_active",
    "chunk_vector_payload",
    "embed_text_bge",
    "intent_vector_payload",
    "reset_bge_model_for_testing",
    "resolve_query_vector",
]
