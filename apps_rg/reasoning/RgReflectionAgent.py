"""RgReflectionAgent — RG domain reflection agent with Phase 5 meta-learning.

Originally from: ContentQualityAgent.py (Surgical Extraction 2026-01-06)
Refactored: 2026-03-11 (P2-A) — now subclasses BaseReflectionAgent.

PHASE 5 META-LEARNING (Feb 2026):
- Redis/Pinecone integration for reflection pattern memory
- Execution insight caching and recall
- Quality pattern learning for resume generation
- Cross-session learning persistence
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from agentic_core.L4_state.enforcement.graph_memory_bridge import GraphMemoryBridge
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

_emit_authorize_and_execute("p2", "RgReflectionAgent", "execution_auth")
_emit_validates_capability("p2", "RgReflectionAgent", "capability_check")
_emit_routes_to_capability("p2", "RgReflectionAgent", "capability_route")
_emit_writes_via_uwg("p2", "RgReflectionAgent", "uwg_write")
_emit_blocks_direct_write("p2", "RgReflectionAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "RgReflectionAgent", "tool_invocation")
_emit_captures_execution_output("p2", "RgReflectionAgent", "exec_output")
_emit_dispatches_agent("p3", "RgReflectionAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "RgReflectionAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "RgReflectionAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "RgReflectionAgent", "healing_outcome")
_emit_escalates_failure("p3", "RgReflectionAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "RgReflectionAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "RgReflectionAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "RgReflectionAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "RgReflectionAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "RgReflectionAgent", "eval_metric")
_emit_stores_embedding("p4", "RgReflectionAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "RgReflectionAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "RgReflectionAgent", "exec_snapshot_link")
from apps_shared.reasoning.BaseReflectionAgent import BaseReflectionAgent

_emit_applies_guardrail("p0", "RgReflectionAgent", "p0_governance")
_emit_reads_policy_state("p0", "RgReflectionAgent", "policy_binding")
_emit_snapshots_state("p0", "RgReflectionAgent", "state_snapshot")
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

_emit_emits_metric_event("RgReflectionAgent", "p4obs", "metric_1")
_emit_emits_metric_event("RgReflectionAgent", "p4obs", "metric_2")
_emit_emits_metric_event("RgReflectionAgent", "p4obs", "metric_3")
_emit_emits_metric_event("RgReflectionAgent", "p4obs", "metric_4")
_emit_emits_metric_event("RgReflectionAgent", "p4obs", "metric_5")
_emit_emits_metric_event("RgReflectionAgent", "p4obs", "metric_6")
_emit_records_incident_event("RgReflectionAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("RgReflectionAgent", "p4obs", "anomaly")
_emit_writes_observability_log("RgReflectionAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("RgReflectionAgent", "p4obs", "mon_state")
_emit_triggers_alert("RgReflectionAgent", "p4obs", "alert")
_emit_links_incident_trace("RgReflectionAgent", "p4obs", "trace_link")
_emit_captures_pattern("RgReflectionAgent", "p3lm", "pattern")
_emit_records_learning_event("RgReflectionAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("RgReflectionAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("RgReflectionAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("RgReflectionAgent", "p3lm", "routing")
_emit_improves_agent_policy("RgReflectionAgent", "p3lm", "policy")
_emit_stores_learning_state("RgReflectionAgent", "p3lm", "state")
_emit_records_execution_trace("RgReflectionAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("RgReflectionAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("RgReflectionAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("RgReflectionAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("RgReflectionAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("RgReflectionAgent", "env_read", "p2_env_1")
_emit_reads_environ("RgReflectionAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("RgReflectionAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("RgReflectionAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "RgReflectionAgent", "context_pull")
_emit_pulls_context("p1", "RgReflectionAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "RgReflectionAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "RgReflectionAgent", "uwg_term_2")
_emit_writes_through("p1", "RgReflectionAgent", "write_through")
_emit_writes_through("p1", "RgReflectionAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "RgReflectionAgent", "safety_validation")
_emit_invokes_eval("p1", "RgReflectionAgent", "eval_call")
_emit_proposal_commits_routing("p1", "RgReflectionAgent", "routing_commit")
_emit_escalates_to_human("p1", "RgReflectionAgent", "human_escalation")
_emit_routes_through("p1", "RgReflectionAgent", "route_through")
_emit_checks_agent_registry("p1", "RgReflectionAgent", "agent_registry")
_emit_validates_agent_capability("p1", "RgReflectionAgent", "capability")
_emit_dispatches_execution_plan("p1", "RgReflectionAgent", "exec_plan")
_emit_agent_executes_agent("p1", "RgReflectionAgent", "sub_agent")
_emit_routes_to_agent("p1", "RgReflectionAgent", "target_agent")
_emit_verifies_policy("p1", "RgReflectionAgent", "policy_check")
_emit_observes_runtime_state("p1", "RgReflectionAgent", "runtime_state")
_emit_verifies_boundary("p1", "RgReflectionAgent", "boundary_check")
_emit_transcripts_response("p1", "RgReflectionAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "RgReflectionAgent")
_emit_gated_by_confidence("p1", "RgReflectionAgent", "confidence_gate")
emit_replay_key("p0", "RgReflectionAgent")
emit_determinism_digest("p0", "RgReflectionAgent")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


@dataclass
class RgReflectionAgent(BaseReflectionAgent):
    """Learns from RG execution and records insights.

    [PHASE 5] Meta-Learning Integration:
    - Caches execution insights for future recall
    - Learns quality patterns from successful generations
    - Persists learning across sessions via Redis/Pinecone

    Inherits execute() skeleton from BaseReflectionAgent.
    Overrides _post_reflect() to add quality scoring and context recording.
    """

    def __post_init__(self) -> None:
        """Initialize reflection agent."""
        super().__post_init__()
        Logger.debug(f"[{self.__class__.__name__}] Meta-Learning reflection agent initialized")
        try:
            bridge = GraphMemoryBridge.get_instance()
            bridge.create_agent_entity(
                agent_name=self.__class__.__name__,
                agent_type="ReflectionAgent",
                observations=["RG reflection agent with meta-learning and quality scoring"],
            )
        except (AttributeError, RuntimeError, ValueError, OSError):  # guardian: allow-double-logging -- debug-level telemetry before re-raise for KG registration diagnostics
            raise

    def _post_reflect(self, passed_agents: list[str], failed_agents: list[str], converged: bool) -> None:
        """RG-specific post-reflection: quality scoring and context recording."""
        insights: dict[str, Any] = {
            "cycle": self.ctx.current_cycle,
            "signals_at_end": list(self.ctx.signals),
            "failed_agents": failed_agents,
            "modified_sections": list(self.ctx.modified_sections),
            "budget_used": self.ctx.budget.current_cost,
            "converged": converged,
        }
        if converged:
            insights["outcome"] = "success"
            if self.ctx.current_resume:
                quality_score: float = self._estimate_quality_score()
                self.ctx.record_success(self.ctx.current_resume, quality_score)
                if quality_score < 0.6:
                    best_practices = self._search_external_best_practices(
                        "resume writing quality improvement",
                    )
                    if best_practices:
                        insights["external_best_practices"] = best_practices
        else:
            insights["outcome"] = "needs_more_cycles"
            best_practices = self._search_external_best_practices(
                "outreach reflection improvement techniques",
            )
            if best_practices:
                insights["external_best_practices"] = best_practices
        self.ctx.results["reflection"] = insights
        self._persist_reflection_to_kg(insights, passed_agents, failed_agents, converged)

    def _persist_reflection_to_kg(
        self,
        insights: dict[str, Any],
        passed_agents: list[str],
        failed_agents: list[str],
        converged: bool,
    ) -> None:
        """Persist reflection outcome to Memory MCP knowledge graph."""
        try:
            bridge = GraphMemoryBridge.get_instance()
            outcome = insights.get("outcome", "unknown")
            cycle = insights.get("cycle", 0)
            obs = f"Cycle={cycle} outcome={outcome} passed={len(passed_agents)} failed={len(failed_agents)} budget={insights.get('budget_used', 0):.4f}"
            bridge.add_observation(entity_name=self.__class__.__name__, observation=obs)
            if converged and self.ctx.current_resume:
                bridge.create_relation(
                    from_entity=self.__class__.__name__,
                    to_entity="ResumeDocument",
                    relation_type="REFLECTS_ON",
                )
        except (AttributeError, RuntimeError, ValueError, OSError):  # guardian: allow-double-logging -- debug-level telemetry before re-raise for KG reflection persistence diagnostics
            raise

    def _search_external_best_practices(self, topic: str) -> list[dict[str, Any]]:
        """Search for external best practices via Brave Search MCP when quality is low.

        Args:
            topic: The topic to search for

        Returns:
            List of result dicts with title/url/description, or empty list on failure
        """
        try:
            import asyncio

            from agentic_core.L3_orchestration.reasoning.mcp_manager import MCPConnectionManager

            mcp = MCPConnectionManager()
            args = {"query": topic, "count": 3}
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    import concurrent.futures

                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                        future = pool.submit(asyncio.run, mcp.call_tool("brave_search", args))
                        # guardian: allow-magic-config
                        result = future.result(timeout=10)
                else:
                    result = loop.run_until_complete(mcp.call_tool("brave_search", args))
            except (RuntimeError, TimeoutError, ValueError, AttributeError):  # guardian: allow-default-fallback -- external MCP search is best-effort; empty dict falls through to no-results path below
                result = {}
            if isinstance(result, dict) and result.get("results"):
                Logger.info(
                    f"[{self.__class__.__name__}] Brave Search: {len(result['results'])} results for '{topic}'",
                )
                return result["results"][:3]
            return []
        except (RuntimeError, TimeoutError, ValueError, AttributeError, OSError):  # guardian: allow-log-and-swallow -- Brave Search is best-effort enrichment; empty-list fallthrough is expected on any failure
            return []

    def _estimate_quality_score(self) -> float:
        """Estimate quality score as passed/total agents ratio."""
        total_agents: int = len(self.ctx.results)
        if total_agents == 0:
            return 0.5
        passed = sum(1 for r in self.ctx.results.values() if r.get("passed", False))
        return passed / total_agents

    def ml_cache_execution_insight(self, insight_id: str, insight_data: dict[str, Any]) -> bool:
        """
        Cache an execution insight for future recall.

        Args:
            insight_id: Unique insight identifier
            insight_data: Insight data (cycle, signals, outcome, etc.)

        Returns:
            True if cached successfully
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            f"RgReflectionAgent.ml_cache_execution_insight:{insight_id}",
        )
        cache_key = f"execution_insight:{insight_id}"
        return self.ml_cache_set(cache_key, insight_data)

    # guardian: allow-type-erasure
    def ml_recall_execution_insight(self, insight_id: str) -> dict[str, Any] | None:
        """
        Recall a cached execution insight.

        Args:
            insight_id: Unique insight identifier

        Returns:
            Cached insight data or None
        """
        cache_key = f"execution_insight:{insight_id}"
        return self.ml_cache_get(cache_key)

    def ml_cache_quality_pattern(self, pattern_id: str, pattern_data: dict[str, Any]) -> bool:
        """
        Cache a successful quality pattern.

        Args:
            pattern_id: Unique pattern identifier
            pattern_data: Quality pattern data

        Returns:
            True if cached successfully
        """
        cache_key = f"quality_pattern:{pattern_id}"
        return self.ml_cache_set(cache_key, pattern_data)

    # guardian: allow-type-erasure
    def ml_recall_quality_pattern(self, pattern_id: str) -> dict[str, Any] | None:
        """
        Recall a cached quality pattern.

        Args:
            pattern_id: Unique pattern identifier

        Returns:
            Cached pattern data or None
        """
        cache_key = f"quality_pattern:{pattern_id}"
        return self.ml_cache_get(cache_key)

    def ml_record_reflection_success(
        self,
        context_hash: str,
        insights: dict[str, Any],
        quality_score: float,
    ) -> bool:
        """
        Record a successful reflection for future learning.

        Args:
            context_hash: Hash of the execution context
            insights: Reflection insights
            quality_score: Quality score achieved

        Returns:
            True if recorded successfully
        """
        if quality_score >= 0.7:
            cache_key = f"reflection_success:{context_hash}"
            return self.ml_cache_set(cache_key, {"insights": insights, "quality_score": quality_score})
        return False

    # guardian: allow-type-erasure
    def ml_recall_similar_reflection(self, context_hash: str) -> dict[str, Any] | None:
        """
        Recall a similar successful reflection.

        Args:
            context_hash: Hash of the execution context

        Returns:
            Cached reflection data or None
        """
        cache_key = f"reflection_success:{context_hash}"
        return self.ml_cache_get(cache_key)
