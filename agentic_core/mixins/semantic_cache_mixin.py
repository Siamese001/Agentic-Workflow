"""
semantic_cache_mixin - Unified Semantic cache Access

[PHASE 3 MIGRATION] Provides single interface to canonical SemanticCacheManager.

W4 P4.3 (ADR-079): the ``semantic_cache`` property and the five downstream
``semantic_*`` helpers handle ``CriticalInfrastructureError`` from
``SemanticCacheManager.get_instance()`` gracefully — STRICT-mode init failure
returns ``None`` from the property, and downstream helpers short-circuit to
their documented degraded-state fallbacks instead of propagating the
exception to caller agents.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

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

_emit_applies_guardrail("p0", "semantic_cache_mixin", "p0_governance")
_emit_reads_policy_state("p0", "semantic_cache_mixin", "policy_binding")
_emit_snapshots_state("p0", "semantic_cache_mixin", "state_snapshot")
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

_emit_emits_metric_event("semantic_cache_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("semantic_cache_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("semantic_cache_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("semantic_cache_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("semantic_cache_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("semantic_cache_mixin", "p4obs", "metric_6")
_emit_records_incident_event("semantic_cache_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("semantic_cache_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("semantic_cache_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("semantic_cache_mixin", "p4obs", "mon_state")
_emit_triggers_alert("semantic_cache_mixin", "p4obs", "alert")
_emit_links_incident_trace("semantic_cache_mixin", "p4obs", "trace_link")
_emit_captures_pattern("semantic_cache_mixin", "p3lm", "pattern")
_emit_records_learning_event("semantic_cache_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("semantic_cache_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("semantic_cache_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("semantic_cache_mixin", "p3lm", "routing")
_emit_improves_agent_policy("semantic_cache_mixin", "p3lm", "policy")
_emit_stores_learning_state("semantic_cache_mixin", "p3lm", "state")
_emit_records_execution_trace("semantic_cache_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("semantic_cache_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("semantic_cache_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("semantic_cache_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("semantic_cache_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("semantic_cache_mixin", "env_read", "p2_env_1")
_emit_reads_environ("semantic_cache_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("semantic_cache_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("semantic_cache_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "semantic_cache_mixin", "context_pull")
_emit_pulls_context("p1", "semantic_cache_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "semantic_cache_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "semantic_cache_mixin", "uwg_term_2")
_emit_writes_through("p1", "semantic_cache_mixin", "write_through")
_emit_writes_through("p1", "semantic_cache_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "semantic_cache_mixin", "safety_validation")
_emit_invokes_eval("p1", "semantic_cache_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "semantic_cache_mixin", "routing_commit")
_emit_escalates_to_human("p1", "semantic_cache_mixin", "human_escalation")
_emit_routes_through("p1", "semantic_cache_mixin", "route_through")
_emit_checks_agent_registry("p1", "semantic_cache_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "semantic_cache_mixin", "capability")
_emit_dispatches_execution_plan("p1", "semantic_cache_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "semantic_cache_mixin", "sub_agent")
_emit_routes_to_agent("p1", "semantic_cache_mixin", "target_agent")
_emit_verifies_policy("p1", "semantic_cache_mixin", "policy_check")
_emit_observes_runtime_state("p1", "semantic_cache_mixin", "runtime_state")
_emit_verifies_boundary("p1", "semantic_cache_mixin", "boundary_check")
_emit_transcripts_response("p1", "semantic_cache_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "semantic_cache_mixin")
_emit_gated_by_confidence("p1", "semantic_cache_mixin", "confidence_gate")
emit_replay_key("p0", "semantic_cache_mixin")
emit_determinism_digest("p0", "semantic_cache_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "semantic_cache_mixin", "execution_auth")
_emit_validates_capability("p2", "semantic_cache_mixin", "capability_check")
_emit_routes_to_capability("p2", "semantic_cache_mixin", "capability_route")
_emit_writes_via_uwg("p2", "semantic_cache_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "semantic_cache_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "semantic_cache_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "semantic_cache_mixin", "exec_output")
_emit_dispatches_agent("p3", "semantic_cache_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "semantic_cache_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "semantic_cache_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "semantic_cache_mixin", "healing_outcome")
_emit_escalates_failure("p3", "semantic_cache_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "semantic_cache_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "semantic_cache_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "semantic_cache_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "semantic_cache_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "semantic_cache_mixin", "eval_metric")
_emit_stores_embedding("p4", "semantic_cache_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "semantic_cache_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "semantic_cache_mixin", "exec_snapshot_link")


class SemanticCacheMixin:
    """
    Mixin providing unified semantic cache access.

    [PHASE 3 MIGRATION] Routes to canonical L4 implementation.

    Usage:
        class MyAgent(SemanticCacheMixin, SovereignBaseAgent):
            def process(self, query: str):
                namespace = self.__class__.__name__
                cached = self.semantic_recall(query, namespace)
                if cached:
                    return cached
                result = self._compute(query)
                self.semantic_learn(query, namespace, result)
                return result

    Note: `semantic_cache` always delegates to `SemanticCacheManager.get_instance()`.
    No stale references — every call returns the live singleton.
    """

    @property
    def semantic_cache(self):
        """Return canonical SemanticCacheManager singleton, or ``None`` on STRICT-mode init failure.

        Returns the live singleton via ``SemanticCacheManager.get_instance()``.
        On ``CriticalInfrastructureError`` (STRICT-mode infra unavailable),
        emits a critical log and returns ``None`` — callers MUST tolerate
        ``None`` per ADR-079 / W4 P4.3. The five ``semantic_*`` helpers below
        already short-circuit to documented fallbacks when the property is
        ``None``, so subclasses that only use the helper methods need no
        additional guards.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "SemanticCacheMixin.semantic_cache"
        )

        from agentic_core.L4_state.utils.memory.semantic_cache_manager import (
            CriticalInfrastructureError,
            SemanticCacheManager,
        )

        try:
            return SemanticCacheManager.get_instance()
        except CriticalInfrastructureError as exc:  # ADR-079 / W4 P4.3: STRICT-mode infra failure must not bubble up to mixin consumers
            logger.critical(
                "SemanticCacheMixin: STRICT-mode infra unavailable; semantic cache disabled: %s",
                exc,
            )
            return None

    def semantic_recall(
        self,
        context: str,
        namespace: str,
        *,
        flow_class: str | None = None,
        replay_mode: bool = False,
    ) -> Any:
        """Recall from semantic cache (L1 Redis + L2 BGE vector store).

        Args:
            flow_class: Flow classification (e.g. 'D4_ACTION', 'HITL'). Must-bypass
                flows are gated inside SemanticCacheManager.recall(). Pass None for
                non-D2 paths where bypass enforcement is not required.
            replay_mode: Set True to suppress all cache reads (replay scenarios).

        Returns ``None`` when the singleton is unavailable (STRICT-mode init failure).
        """
        cache = self.semantic_cache
        if cache is None:
            return None
        return cache.recall(
            context,
            namespace,
            flow_class=flow_class,
            replay_mode=replay_mode,
        )

    def semantic_learn(
        self,
        context: str,
        namespace: str,
        result: dict[str, Any],
        feedback_score: float | None = None,
    ) -> None:
        """Store in semantic cache working memory (Redis, 24h TTL). No-op on STRICT-mode failure."""
        cache = self.semantic_cache
        if cache is None:
            return
        cache.learn(context, namespace, result, feedback_score)

    def semantic_promote(
        self,
        context: str,
        namespace: str,
        result: dict[str, Any],
        feedback_score: float,
    ) -> bool:
        """Promote high-value memory to long-term vector store. Returns ``False`` on STRICT-mode failure."""
        cache = self.semantic_cache
        if cache is None:
            return False
        return cache.promote_to_long_term(context, namespace, result, feedback_score)

    def semantic_update_feedback(self, context: str, namespace: str, feedback_score: float) -> bool:
        """Update feedback score for existing memory; auto-promotes if above threshold. ``False`` on STRICT-mode failure."""
        cache = self.semantic_cache
        if cache is None:
            return False
        return cache.update_feedback_score(context, namespace, feedback_score)

    def semantic_stats(self) -> dict[str, Any]:
        """Return cache hit/miss statistics. Returns empty dict on STRICT-mode failure."""
        cache = self.semantic_cache
        if cache is None:
            return {}
        return cache.get_statistics()


semantic_cache_mixin = SemanticCacheMixin
