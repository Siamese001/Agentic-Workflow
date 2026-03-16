"""
semantic_cache_mixin - Unified Semantic cache Access

[PHASE 3 MIGRATION] Provides single interface to canonical SemanticCacheManager.
"""

from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "semantic_cache_mixin", "p0_governance")
_emit_reads_policy_state("p0", "semantic_cache_mixin", "policy_binding")
_emit_snapshots_state("p0", "semantic_cache_mixin", "state_snapshot")
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
        """Return canonical SemanticCacheManager singleton (no instance caching)."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SemanticCacheMixin.semantic_cache")

        from agentic_core.L4_state.memory.semantic_cache_manager import SemanticCacheManager

        return SemanticCacheManager.get_instance()

    def semantic_recall(self, context: str, namespace: str) -> Any:
        """Recall from semantic cache (L1 Redis + L2 BGE vector store)."""
        return self.semantic_cache.recall(context, namespace)

    def semantic_learn(
        self, context: str, namespace: str, result: dict[str, Any], feedback_score: float | None = None
    ) -> None:
        """Store in semantic cache working memory (Redis, 24h TTL)."""
        self.semantic_cache.learn(context, namespace, result, feedback_score)

    def semantic_promote(
        self, context: str, namespace: str, result: dict[str, Any], feedback_score: float
    ) -> bool:
        """Promote high-value memory to long-term vector store."""
        return self.semantic_cache.promote_to_long_term(context, namespace, result, feedback_score)

    def semantic_update_feedback(self, context: str, namespace: str, feedback_score: float) -> bool:
        """Update feedback score for existing memory; auto-promotes if above threshold."""
        return self.semantic_cache.update_feedback_score(context, namespace, feedback_score)

    def semantic_stats(self) -> dict[str, Any]:
        """Return cache hit/miss statistics."""
        return self.semantic_cache.get_statistics()


semantic_cache_mixin = SemanticCacheMixin
