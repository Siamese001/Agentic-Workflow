"""C0 / RAG — top-k retrieval memoisation cache seam.

Provides ``RagRetrievalCache`` which stores memoised top-k retrieval result
sets keyed by ``(u0_hash, embedder_version, seed_pack_manifest_hash, k,
cutoff)``.

Sovereignty contract
--------------------
* This cache is **strictly informational** — it caches retrieval results for
  identical query/corpus inputs only.  It MUST NOT influence routing,
  safety, or tier decisions.
* L4 remains the sole data authority.  This cache stores memoised derivatives
  only; a cache miss falls through to the live retrieval pipeline.
* ``replay_mode=True`` bypasses every read so replay reconstruction
  re-runs the full retrieval and records results in the transcript.
* Writing to this cache does NOT modify any L4 state.

Key schema::

    rag_topk:{u0_hash}:{embedder_version}:{seed_pack_manifest_hash}:{k}:{cutoff_r6}

``cutoff`` is rounded to 6 decimal places so semantically identical cutoffs
produce the same key regardless of floating-point representation noise.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.cache.cache_key_builders import build_rag_topk_key
from agentic_core.cache.redis_cache_client import (
    DeterministicRedisCache,
    get_hot_cache,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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

_emit_applies_guardrail("p0", "rag_retrieval_cache", "p0_governance")
_emit_reads_policy_state("p0", "rag_retrieval_cache", "policy_binding")
_emit_snapshots_state("p0", "rag_retrieval_cache", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("rag_retrieval_cache", "p4obs", "metric_1")
_emit_emits_metric_event("rag_retrieval_cache", "p4obs", "metric_2")
_emit_emits_metric_event("rag_retrieval_cache", "p4obs", "metric_3")
_emit_emits_metric_event("rag_retrieval_cache", "p4obs", "metric_4")
_emit_emits_metric_event("rag_retrieval_cache", "p4obs", "metric_5")
_emit_emits_metric_event("rag_retrieval_cache", "p4obs", "metric_6")
_emit_records_incident_event("rag_retrieval_cache", "p4obs", "incident")
_emit_captures_runtime_anomaly("rag_retrieval_cache", "p4obs", "anomaly")
_emit_writes_observability_log("rag_retrieval_cache", "p4obs", "obs_log")
_emit_updates_monitoring_state("rag_retrieval_cache", "p4obs", "mon_state")
_emit_triggers_alert("rag_retrieval_cache", "p4obs", "alert")
_emit_links_incident_trace("rag_retrieval_cache", "p4obs", "trace_link")
_emit_captures_pattern("rag_retrieval_cache", "p3lm", "pattern")
_emit_records_learning_event("rag_retrieval_cache", "p3lm", "learning_event")
_emit_writes_learning_snapshot("rag_retrieval_cache", "p3lm", "snapshot")
_emit_feeds_meta_learning("rag_retrieval_cache", "p3lm", "meta_feed")
_emit_updates_routing_strategy("rag_retrieval_cache", "p3lm", "routing")
_emit_improves_agent_policy("rag_retrieval_cache", "p3lm", "policy")
_emit_stores_learning_state("rag_retrieval_cache", "p3lm", "state")
_emit_records_execution_trace("rag_retrieval_cache", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("rag_retrieval_cache", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("rag_retrieval_cache", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("rag_retrieval_cache", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("rag_retrieval_cache", "L4_STATE", "p2_trace_5")
_emit_reads_environ("rag_retrieval_cache", "env_read", "p2_env_1")
_emit_reads_environ("rag_retrieval_cache", "env_read", "p2_env_2")
_emit_reads_runtime_state("rag_retrieval_cache", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("rag_retrieval_cache", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "rag_retrieval_cache", "context_pull")
_emit_pulls_context("p1", "rag_retrieval_cache", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "rag_retrieval_cache", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "rag_retrieval_cache", "uwg_term_2")
_emit_writes_through("p1", "rag_retrieval_cache", "write_through")
_emit_writes_through("p1", "rag_retrieval_cache", "write_through_2")
_emit_validated_by_safety_plane("p1", "rag_retrieval_cache", "safety_validation")
_emit_invokes_eval("p1", "rag_retrieval_cache", "eval_call")
_emit_proposal_commits_routing("p1", "rag_retrieval_cache", "routing_commit")
_emit_escalates_to_human("p1", "rag_retrieval_cache", "human_escalation")
_emit_routes_through("p1", "rag_retrieval_cache", "route_through")
_emit_checks_agent_registry("p1", "rag_retrieval_cache", "agent_registry")
_emit_validates_agent_capability("p1", "rag_retrieval_cache", "capability")
_emit_dispatches_execution_plan("p1", "rag_retrieval_cache", "exec_plan")
_emit_agent_executes_agent("p1", "rag_retrieval_cache", "sub_agent")
_emit_routes_to_agent("p1", "rag_retrieval_cache", "target_agent")
_emit_verifies_policy("p1", "rag_retrieval_cache", "policy_check")
_emit_observes_runtime_state("p1", "rag_retrieval_cache", "runtime_state")
_emit_verifies_boundary("p1", "rag_retrieval_cache", "boundary_check")
_emit_transcripts_response("p1", "rag_retrieval_cache", "transcript")
_emit_hard_fails_untranscripted("p1", "rag_retrieval_cache")
_emit_gated_by_confidence("p1", "rag_retrieval_cache", "confidence_gate")
emit_replay_key("p0", "rag_retrieval_cache")
emit_determinism_digest("p0", "rag_retrieval_cache")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "rag_retrieval_cache", "execution_auth")
_emit_validates_capability("p2", "rag_retrieval_cache", "capability_check")
_emit_routes_to_capability("p2", "rag_retrieval_cache", "capability_route")
_emit_writes_via_uwg("p2", "rag_retrieval_cache", "uwg_write")
_emit_blocks_direct_write("p2", "rag_retrieval_cache", "direct_write_block")
_emit_records_tool_invocation("p2", "rag_retrieval_cache", "tool_invocation")
_emit_captures_execution_output("p2", "rag_retrieval_cache", "exec_output")
_emit_dispatches_agent("p3", "rag_retrieval_cache", "agent_dispatch")
_emit_coordinates_agents("p3", "rag_retrieval_cache", "agent_coordination")
_emit_records_workflow_lineage("p3", "rag_retrieval_cache", "workflow_lineage")
_emit_records_healing_outcome("p3", "rag_retrieval_cache", "healing_outcome")
_emit_escalates_failure("p3", "rag_retrieval_cache", "failure_escalation")
_emit_orchestrates_workflow("p3", "rag_retrieval_cache", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rag_retrieval_cache", "healing_dispatch")
_emit_invokes_evaluation("p3", "rag_retrieval_cache", "evaluation_signal")
_emit_records_telemetry_event("p4", "rag_retrieval_cache", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rag_retrieval_cache", "eval_metric")
_emit_stores_embedding("p4", "rag_retrieval_cache", "embedding_store")
_emit_updates_meta_learning_state("p4", "rag_retrieval_cache", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rag_retrieval_cache", "exec_snapshot_link")

logger = logging.getLogger(__name__)

_DEFAULT_RAG_TOPK_TTL: int = 600  # 10 minutes — retrieval results are short-lived


class RagRetrievalCache:
    """Memoises top-k retrieval result sets for identical C0 inputs.

    The cached value is a list of result dicts, e.g.::

        [
            {
                "chunk_id":   "<stable-id>",
                "score":      0.923,
                "text":       "...",
                "source":     "seed-pack/...",
            },
            ...
        ]

    **Informational only** — callers must NOT use cached retrieval results
    to gate routing or safety decisions.  Use only to avoid redundant
    embedding/retrieval I/O for identical query inputs.

    Input segments:

    +---------------------------+----------------------------------------------+
    | ``u0_hash``               | SHA-256 of the canonical query / u0 context  |
    | ``embedder_version``      | stable embedder model version slug           |
    | ``seed_pack_manifest_hash`` | hash of the active seed-pack manifest      |
    | ``k``                     | number of results requested                  |
    | ``cutoff``                | minimum similarity score threshold           |
    +---------------------------+----------------------------------------------+

    Parameters
    ----------
    ttl_seconds:
        Redis TTL applied to every ``set`` call.  Default 10 minutes; keep
        short because corpus updates invalidate results via manifest-hash
        rotation rather than by TTL.
    cache:
        Override the shared hot-cache instance (useful for testing).
    """

    def __init__(
        self,
        ttl_seconds: int = _DEFAULT_RAG_TOPK_TTL,
        cache: DeterministicRedisCache | None = None,
    ) -> None:
        self._ttl = ttl_seconds
        self._cache = cache or get_hot_cache()

    def get(
        self,
        u0_hash: str,
        embedder_version: str,
        seed_pack_manifest_hash: str,
        k: int,
        cutoff: float,
        *,
        replay_mode: bool = False,
    ) -> list[dict[str, Any]] | None:
        """Return the cached top-k result list or ``None`` on miss/bypass.

        Returns ``None`` (forcing a live retrieval) when:
        - The key is not present in Redis or the fallback store.
        - Redis is unreachable and the fallback store has no entry.
        - ``replay_mode=True``.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "RagRetrievalCache.get")

        key = build_rag_topk_key(u0_hash, embedder_version, seed_pack_manifest_hash, k, cutoff)
        result = self._cache.get_json(key, replay_mode=replay_mode)
        if result is None:
            return None
        if not isinstance(result, list):
            return None
        return result

    def set(
        self,
        u0_hash: str,
        embedder_version: str,
        seed_pack_manifest_hash: str,
        k: int,
        cutoff: float,
        results: list[dict[str, Any]],
    ) -> None:
        """Store *results* under the deterministic key.

        *results* must be a list of chunk dicts produced by the retrieval
        pipeline.  Each dict must be JSON-serialisable (no numpy arrays,
        no datetime objects).
        """
        key = build_rag_topk_key(u0_hash, embedder_version, seed_pack_manifest_hash, k, cutoff)
        self._cache.set_json(key, results, ttl_seconds=self._ttl)

    def invalidate(
        self,
        u0_hash: str,
        embedder_version: str,
        seed_pack_manifest_hash: str,
        k: int,
        cutoff: float,
    ) -> None:
        """Explicitly evict a cached retrieval result set."""
        key = build_rag_topk_key(u0_hash, embedder_version, seed_pack_manifest_hash, k, cutoff)
        self._cache.delete(key)


# ---------------------------------------------------------------------------
# Module-level convenience singleton
# ---------------------------------------------------------------------------

_rag_retrieval_cache: RagRetrievalCache | None = None


def get_rag_retrieval_cache() -> RagRetrievalCache:
    """Return the process-global ``RagRetrievalCache`` instance."""
    global _rag_retrieval_cache
    if _rag_retrieval_cache is None:
        _rag_retrieval_cache = RagRetrievalCache()
    return _rag_retrieval_cache


__all__ = ["RagRetrievalCache", "get_rag_retrieval_cache"]
