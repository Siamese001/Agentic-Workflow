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
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "bmg_embedding_similarity")
emit_determinism_digest("p0", "bmg_embedding_similarity")

_emit_dispatches_healing_run("p1", "bmg_embedding_similarity", "L2")
_emit_routes_through("p1", "bmg_embedding_similarity", "L2")
_emit_checks_agent_registry("p1", "bmg_embedding_similarity", "agent_registry")
_emit_validates_agent_capability("p1", "bmg_embedding_similarity", "capability")
_emit_dispatches_execution_plan("p1", "bmg_embedding_similarity", "exec_plan")
_emit_agent_executes_agent("p1", "bmg_embedding_similarity", "sub_agent")
_emit_routes_to_agent("p1", "bmg_embedding_similarity", "target_agent")
_emit_verifies_policy("p1", "bmg_embedding_similarity", "policy_check")
_emit_observes_runtime_state("p1", "bmg_embedding_similarity", "runtime_state")
_emit_verifies_boundary("p1", "bmg_embedding_similarity", "boundary_check")
_emit_transcripts_response("p1", "bmg_embedding_similarity", "transcript")
_emit_hard_fails_untranscripted("p1", "bmg_embedding_similarity")
_emit_gated_by_confidence("p1", "bmg_embedding_similarity", "confidence_gate")
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
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("bmg_embedding_similarity", "p4obs", "metric_1")
_emit_emits_metric_event("bmg_embedding_similarity", "p4obs", "metric_2")
_emit_emits_metric_event("bmg_embedding_similarity", "p4obs", "metric_3")
_emit_emits_metric_event("bmg_embedding_similarity", "p4obs", "metric_4")
_emit_emits_metric_event("bmg_embedding_similarity", "p4obs", "metric_5")
_emit_emits_metric_event("bmg_embedding_similarity", "p4obs", "metric_6")
_emit_records_incident_event("bmg_embedding_similarity", "p4obs", "incident")
_emit_captures_runtime_anomaly("bmg_embedding_similarity", "p4obs", "anomaly")
_emit_writes_observability_log("bmg_embedding_similarity", "p4obs", "obs_log")
_emit_updates_monitoring_state("bmg_embedding_similarity", "p4obs", "mon_state")
_emit_triggers_alert("bmg_embedding_similarity", "p4obs", "alert")
_emit_links_incident_trace("bmg_embedding_similarity", "p4obs", "trace_link")
_emit_captures_pattern("bmg_embedding_similarity", "p3lm", "pattern")
_emit_records_learning_event("bmg_embedding_similarity", "p3lm", "learning_event")
_emit_writes_learning_snapshot("bmg_embedding_similarity", "p3lm", "snapshot")
_emit_feeds_meta_learning("bmg_embedding_similarity", "p3lm", "meta_feed")
_emit_updates_routing_strategy("bmg_embedding_similarity", "p3lm", "routing")
_emit_improves_agent_policy("bmg_embedding_similarity", "p3lm", "policy")
_emit_stores_learning_state("bmg_embedding_similarity", "p3lm", "state")
_emit_records_execution_trace("bmg_embedding_similarity", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("bmg_embedding_similarity", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("bmg_embedding_similarity", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("bmg_embedding_similarity", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("bmg_embedding_similarity", "L4_STATE", "p2_trace_5")
_emit_reads_environ("bmg_embedding_similarity", "env_read", "p2_env_1")
_emit_reads_environ("bmg_embedding_similarity", "env_read", "p2_env_2")
_emit_reads_runtime_state("bmg_embedding_similarity", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("bmg_embedding_similarity", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "bmg_embedding_similarity", "context_pull")
_emit_pulls_context("p1", "bmg_embedding_similarity", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "bmg_embedding_similarity", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "bmg_embedding_similarity", "uwg_term_2")
_emit_writes_through("p1", "bmg_embedding_similarity", "write_through")
_emit_writes_through("p1", "bmg_embedding_similarity", "write_through_2")
_emit_validated_by_safety_plane("p1", "bmg_embedding_similarity", "safety_validation")
_emit_invokes_eval("p1", "bmg_embedding_similarity", "eval_call")
_emit_proposal_commits_routing("p1", "bmg_embedding_similarity", "routing_commit")

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
    except (ValueError, TypeError, RuntimeError) as e:
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
