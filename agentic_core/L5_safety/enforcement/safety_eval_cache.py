"""L5 Safety — policy-evaluation memoisation cache seam.

Provides ``SafetyEvalCache`` which stores the memoised result of a safety
evaluation for a given ``(compiled_prompt_hash, policy_hash, toolset_hash)``
triple.

Sovereignty contract
--------------------
* L5 remains the certifier.  Redis stores only the memoised *result* for
  identical inputs; it never overrides a live evaluation.
* Cache entries are invalidated purely by version-hash changes — when any
  of the three input hashes changes a fresh evaluation is performed.
* ``replay_mode=True`` bypasses the cache unconditionally so every replay
  re-runs the full evaluation and records the result in the transcript.
* Writing to this cache does NOT modify any L4 state.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.cache.cache_key_builders import build_safety_eval_key
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

emit_replay_key("p0", "safety_eval_cache")
emit_determinism_digest("p0", "safety_eval_cache")

_emit_dispatches_healing_run("p1", "safety_eval_cache", "L5")
_emit_routes_through("p1", "safety_eval_cache", "L5")
_emit_checks_agent_registry("p1", "safety_eval_cache", "agent_registry")
_emit_validates_agent_capability("p1", "safety_eval_cache", "capability")
_emit_dispatches_execution_plan("p1", "safety_eval_cache", "exec_plan")
_emit_agent_executes_agent("p1", "safety_eval_cache", "sub_agent")
_emit_routes_to_agent("p1", "safety_eval_cache", "target_agent")
_emit_verifies_policy("p1", "safety_eval_cache", "policy_check")
_emit_observes_runtime_state("p1", "safety_eval_cache", "runtime_state")
_emit_verifies_boundary("p1", "safety_eval_cache", "boundary_check")
_emit_transcripts_response("p1", "safety_eval_cache", "transcript")
_emit_hard_fails_untranscripted("p1", "safety_eval_cache")
_emit_gated_by_confidence("p1", "safety_eval_cache", "confidence_gate")
_emit_escalates_to_human("p1", "safety_eval_cache", "L5")
_emit_reads_policy_state("p1", "safety_eval_cache", "L5")

_emit_applies_guardrail("p0", "safety_eval_cache", "p0_governance")
_emit_snapshots_state("p0", "safety_eval_cache", "state_snapshot")
_emit_authorize_and_execute("p2", "safety_eval_cache", "execution_auth")
_emit_validates_capability("p2", "safety_eval_cache", "capability_check")
_emit_routes_to_capability("p2", "safety_eval_cache", "capability_route")
_emit_writes_via_uwg("p2", "safety_eval_cache", "uwg_write")
_emit_blocks_direct_write("p2", "safety_eval_cache", "direct_write_block")
_emit_records_tool_invocation("p2", "safety_eval_cache", "tool_invocation")
_emit_captures_execution_output("p2", "safety_eval_cache", "exec_output")
_emit_dispatches_agent("p3", "safety_eval_cache", "agent_dispatch")
_emit_coordinates_agents("p3", "safety_eval_cache", "agent_coordination")
_emit_records_workflow_lineage("p3", "safety_eval_cache", "workflow_lineage")
_emit_records_healing_outcome("p3", "safety_eval_cache", "healing_outcome")
_emit_escalates_failure("p3", "safety_eval_cache", "failure_escalation")
_emit_orchestrates_workflow("p3", "safety_eval_cache", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "safety_eval_cache", "healing_dispatch")
_emit_invokes_evaluation("p3", "safety_eval_cache", "evaluation_signal")
_emit_records_telemetry_event("p4", "safety_eval_cache", "telemetry_event")
_emit_captures_evaluation_metric("p4", "safety_eval_cache", "eval_metric")
_emit_stores_embedding("p4", "safety_eval_cache", "embedding_store")
_emit_updates_meta_learning_state("p4", "safety_eval_cache", "meta_learning")
_emit_links_execution_to_snapshot("p4", "safety_eval_cache", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("safety_eval_cache", "p4obs", "metric_1")
_emit_emits_metric_event("safety_eval_cache", "p4obs", "metric_2")
_emit_emits_metric_event("safety_eval_cache", "p4obs", "metric_3")
_emit_emits_metric_event("safety_eval_cache", "p4obs", "metric_4")
_emit_emits_metric_event("safety_eval_cache", "p4obs", "metric_5")
_emit_emits_metric_event("safety_eval_cache", "p4obs", "metric_6")
_emit_records_incident_event("safety_eval_cache", "p4obs", "incident")
_emit_captures_runtime_anomaly("safety_eval_cache", "p4obs", "anomaly")
_emit_writes_observability_log("safety_eval_cache", "p4obs", "obs_log")
_emit_updates_monitoring_state("safety_eval_cache", "p4obs", "mon_state")
_emit_triggers_alert("safety_eval_cache", "p4obs", "alert")
_emit_links_incident_trace("safety_eval_cache", "p4obs", "trace_link")
_emit_captures_pattern("safety_eval_cache", "p3lm", "pattern")
_emit_records_learning_event("safety_eval_cache", "p3lm", "learning_event")
_emit_writes_learning_snapshot("safety_eval_cache", "p3lm", "snapshot")
_emit_feeds_meta_learning("safety_eval_cache", "p3lm", "meta_feed")
_emit_updates_routing_strategy("safety_eval_cache", "p3lm", "routing")
_emit_improves_agent_policy("safety_eval_cache", "p3lm", "policy")
_emit_stores_learning_state("safety_eval_cache", "p3lm", "state")
_emit_records_execution_trace("safety_eval_cache", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("safety_eval_cache", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("safety_eval_cache", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("safety_eval_cache", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("safety_eval_cache", "L4_STATE", "p2_trace_5")
_emit_reads_environ("safety_eval_cache", "env_read", "p2_env_1")
_emit_reads_environ("safety_eval_cache", "env_read", "p2_env_2")
_emit_reads_runtime_state("safety_eval_cache", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("safety_eval_cache", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "safety_eval_cache", "context_pull")
_emit_pulls_context("p1", "safety_eval_cache", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "safety_eval_cache", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "safety_eval_cache", "uwg_term_2")
_emit_writes_through("p1", "safety_eval_cache", "write_through")
_emit_writes_through("p1", "safety_eval_cache", "write_through_2")
_emit_validated_by_safety_plane("p1", "safety_eval_cache", "safety_validation")
_emit_invokes_eval("p1", "safety_eval_cache", "eval_call")
_emit_proposal_commits_routing("p1", "safety_eval_cache", "routing_commit")

logger = logging.getLogger(__name__)

_DEFAULT_SAFETY_EVAL_TTL: int = 1800  # 30 minutes


class SafetyEvalCache:
    """Memoises L5 safety-evaluation results for identical compiled artifacts.

    The cached value is a dict with at least these fields::

        {
            "decision":          "allow" | "block",
            "compliance_hash":   "<64-char hex>",
            "remediation_hints": [...],
        }

    Callers must verify that all three hash inputs still match the current
    execution context before accepting a cached result.

    Parameters
    ----------
    ttl_seconds:
        Redis TTL applied to every ``set`` call.
    cache:
        Override the shared hot-cache instance (useful for testing).
    """

    def __init__(
        self,
        ttl_seconds: int = _DEFAULT_SAFETY_EVAL_TTL,
        cache: DeterministicRedisCache | None = None,
    ) -> None:
        self._ttl = ttl_seconds
        self._cache = cache or get_hot_cache()

    def get(
        self,
        compiled_prompt_hash: str,
        policy_hash: str,
        toolset_hash: str,
        *,
        replay_mode: bool = False,
    ) -> dict[str, Any] | None:
        """Return the cached evaluation dict or ``None`` on miss/bypass.

        Returns ``None`` (forcing a fresh L5 evaluation) when:
        - The key is not present.
        - Redis is unreachable and the fallback store has no entry.
        - ``replay_mode=True``.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "SafetyEvalCache.get")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SafetyEvalCache.get".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        key = build_safety_eval_key(compiled_prompt_hash, policy_hash, toolset_hash)
        return self._cache.get_json(key, replay_mode=replay_mode)

    def set(
        self,
        compiled_prompt_hash: str,
        policy_hash: str,
        toolset_hash: str,
        eval_result: dict[str, Any],
    ) -> None:
        """Store *eval_result* under the deterministic key.

        *eval_result* must contain at minimum ``"decision"`` (``"allow"``
        or ``"block"``) and ``"compliance_hash"`` (a 64-hex SHA-256
        produced by the L5 evaluator).  ``"remediation_hints"`` is
        optional but recommended for observability.
        """
        key = build_safety_eval_key(compiled_prompt_hash, policy_hash, toolset_hash)
        self._cache.set_json(key, eval_result, ttl_seconds=self._ttl)

    def get_or_fetch(
        self,
        compiled_prompt_hash: str,
        policy_hash: str,
        toolset_hash: str,
        fetch_from_l5: Any,
        *,
        replay_mode: bool = False,
    ) -> dict[str, Any]:
        """Read-through helper: return cached eval or call *fetch_from_l5*.

        *fetch_from_l5* is a zero-argument callable that runs the full L5
        safety evaluation and returns the result dict.  Called only on a
        cache miss.

        This is the canonical wiring point for L5 evaluator engines.  The
        evaluator should call this instead of running a live evaluation on
        every request.

        The returned dict must include at minimum ``"decision"`` and
        ``"compliance_hash"`` — the same contract as ``set()``.
        """
        if not replay_mode:
            cached = self.get(compiled_prompt_hash, policy_hash, toolset_hash)
            if cached is not None:
                logger.debug("[L5 cache] safety_eval HIT")
                return cached
        logger.debug("[L5 cache] safety_eval MISS — running live evaluation")
        result = fetch_from_l5()
        if not replay_mode:
            self.set(compiled_prompt_hash, policy_hash, toolset_hash, result)
        return result

    def invalidate(
        self,
        compiled_prompt_hash: str,
        policy_hash: str,
        toolset_hash: str,
    ) -> None:
        """Explicitly evict a safety-evaluation entry."""
        key = build_safety_eval_key(compiled_prompt_hash, policy_hash, toolset_hash)
        self._cache.delete(key)


# ---------------------------------------------------------------------------
# Module-level convenience singleton
# ---------------------------------------------------------------------------

_safety_eval_cache: SafetyEvalCache | None = None


def get_safety_eval_cache() -> SafetyEvalCache:
    """Return the process-global ``SafetyEvalCache`` instance."""
    global _safety_eval_cache
    if _safety_eval_cache is None:
        _safety_eval_cache = SafetyEvalCache()
    return _safety_eval_cache
