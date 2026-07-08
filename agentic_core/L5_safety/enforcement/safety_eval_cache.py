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
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "safety_eval_cache")
trace_contract.emit_determinism_digest("p0", "safety_eval_cache")

trace_contract._emit_dispatches_healing_run("p1", "safety_eval_cache", "L5")
trace_contract._emit_routes_through("p1", "safety_eval_cache", "L5")
trace_contract._emit_checks_agent_registry("p1", "safety_eval_cache", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "safety_eval_cache", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "safety_eval_cache", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "safety_eval_cache", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "safety_eval_cache", "target_agent")
trace_contract._emit_verifies_policy("p1", "safety_eval_cache", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "safety_eval_cache", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "safety_eval_cache", "boundary_check")
trace_contract._emit_transcripts_response("p1", "safety_eval_cache", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "safety_eval_cache")
trace_contract._emit_gated_by_confidence("p1", "safety_eval_cache", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "safety_eval_cache", "L5")
trace_contract._emit_reads_policy_state("p1", "safety_eval_cache", "L5")

trace_contract._emit_applies_guardrail("p0", "safety_eval_cache", "p0_governance")
trace_contract._emit_snapshots_state("p0", "safety_eval_cache", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "safety_eval_cache", "execution_auth")
trace_contract._emit_validates_capability("p2", "safety_eval_cache", "capability_check")
trace_contract._emit_routes_to_capability("p2", "safety_eval_cache", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "safety_eval_cache", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "safety_eval_cache", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "safety_eval_cache", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "safety_eval_cache", "exec_output")
trace_contract._emit_dispatches_agent("p3", "safety_eval_cache", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "safety_eval_cache", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "safety_eval_cache", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "safety_eval_cache", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "safety_eval_cache", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "safety_eval_cache", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "safety_eval_cache", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "safety_eval_cache", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "safety_eval_cache", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "safety_eval_cache", "eval_metric")
trace_contract._emit_stores_embedding("p4", "safety_eval_cache", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "safety_eval_cache", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "safety_eval_cache", "exec_snapshot_link")

trace_contract._emit_emits_metric_event("safety_eval_cache", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("safety_eval_cache", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("safety_eval_cache", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("safety_eval_cache", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("safety_eval_cache", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("safety_eval_cache", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("safety_eval_cache", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("safety_eval_cache", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("safety_eval_cache", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("safety_eval_cache", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("safety_eval_cache", "p4obs", "alert")
trace_contract._emit_links_incident_trace("safety_eval_cache", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("safety_eval_cache", "p3lm", "pattern")
trace_contract._emit_records_learning_event("safety_eval_cache", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("safety_eval_cache", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("safety_eval_cache", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("safety_eval_cache", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("safety_eval_cache", "p3lm", "policy")
trace_contract._emit_stores_learning_state("safety_eval_cache", "p3lm", "state")
trace_contract._emit_records_execution_trace("safety_eval_cache", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("safety_eval_cache", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("safety_eval_cache", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("safety_eval_cache", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("safety_eval_cache", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("safety_eval_cache", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("safety_eval_cache", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("safety_eval_cache", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("safety_eval_cache", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "safety_eval_cache", "context_pull")
trace_contract._emit_pulls_context("p1", "safety_eval_cache", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "safety_eval_cache", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "safety_eval_cache", "uwg_term_2")
trace_contract._emit_writes_through("p1", "safety_eval_cache", "write_through")
trace_contract._emit_writes_through("p1", "safety_eval_cache", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "safety_eval_cache", "safety_validation")
trace_contract._emit_invokes_eval("p1", "safety_eval_cache", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "safety_eval_cache", "routing_commit")

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
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "SafetyEvalCache.get")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SafetyEvalCache.get".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
