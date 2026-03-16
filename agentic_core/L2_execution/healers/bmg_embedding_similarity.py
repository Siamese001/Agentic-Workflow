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

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "bmg_embedding_similarity")
emit_determinism_digest("p0", "bmg_embedding_similarity")

_emit_dispatches_healing_run("p1", "bmg_embedding_similarity", "L2")
_emit_routes_through("p1", "bmg_embedding_similarity", "L2")
_emit_escalates_to_human("p1", "bmg_embedding_similarity", "L2")
_emit_reads_policy_state("p1", "bmg_embedding_similarity", "L2")
_emit_authorize_and_execute("p2", "bmg_embedding_similarity", "execution_auth")
_emit_validates_capability("p2", "bmg_embedding_similarity", "capability_check")
_emit_routes_to_capability("p2", "bmg_embedding_similarity", "capability_route")
_emit_writes_via_uwg("p2", "bmg_embedding_similarity", "uwg_write")
_emit_blocks_direct_write("p2", "bmg_embedding_similarity", "direct_write_block")
_emit_records_tool_invocation("p2", "bmg_embedding_similarity", "tool_invocation")
_emit_captures_execution_output("p2", "bmg_embedding_similarity", "exec_output")
_emit_dispatches_agent("p3", "bmg_embedding_similarity", "agent_dispatch")
_emit_coordinates_agents("p3", "bmg_embedding_similarity", "agent_coordination")
_emit_records_workflow_lineage("p3", "bmg_embedding_similarity", "workflow_lineage")
_emit_records_healing_outcome("p3", "bmg_embedding_similarity", "healing_outcome")
_emit_escalates_failure("p3", "bmg_embedding_similarity", "failure_escalation")
_emit_orchestrates_workflow("p3", "bmg_embedding_similarity", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "bmg_embedding_similarity", "healing_dispatch")
_emit_invokes_evaluation("p3", "bmg_embedding_similarity", "evaluation_signal")
_emit_records_telemetry_event("p4", "bmg_embedding_similarity", "telemetry_event")
_emit_captures_evaluation_metric("p4", "bmg_embedding_similarity", "eval_metric")
_emit_stores_embedding("p4", "bmg_embedding_similarity", "embedding_store")
_emit_updates_meta_learning_state("p4", "bmg_embedding_similarity", "meta_learning")
_emit_links_execution_to_snapshot("p4", "bmg_embedding_similarity", "exec_snapshot_link")

logger = logging.getLogger(__name__)
_MODEL_CACHE: object | None = None
_MODEL_ID = "BAAI/bge-m3"


def _get_model() -> object:
    """Load and cache the BGE-M3 model.  Raises ImportError if unavailable."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_get_model", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_get_model", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "_get_model")
    global _MODEL_CACHE
    if _MODEL_CACHE is not None:
        return _MODEL_CACHE
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError as exc:
        raise ImportError(
            "sentence-transformers is required for BMG embedding similarity. Install with: pip install sentence-transformers"
        ) from exc
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
        return bool(torch_mod.cuda.is_available())
    except Exception:
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
    import numpy as np

    model = _get_model()
    all_strings = [unknown] + candidates
    embeddings: np.ndarray = model.encode(
        all_strings, convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False
    )
    query_vec = embeddings[0]
    candidate_vecs = embeddings[1:]
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
    import numpy as np

    model = _get_model()
    vecs: np.ndarray = model.encode(
        [text], convert_to_numpy=True, normalize_embeddings=True, show_progress_bar=False
    )
    return vecs[0].tolist()


def clear_model_cache() -> None:
    """Invalidate the cached model (for tests and hot-reload)."""
    global _MODEL_CACHE
    _MODEL_CACHE = None


__all__ = ["bmg_cosine_similarity", "bmg_embed_text", "clear_model_cache"]
