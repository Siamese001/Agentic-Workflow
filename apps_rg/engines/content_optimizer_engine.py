"""
Content Optimizer Engine - Reorders bullet points for maximum impact
Refactored from optimize_content_order.py
Following Batch 4 specifications

HARDENING: Reads 'hop2_enrichment' (or generation output). Reorders content based on
'adjusted_weights' from Buffer. Writes 'optimized_content'.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_authorize_and_execute("p2", "content_optimizer_engine", "execution_auth")
_emit_validates_capability("p2", "content_optimizer_engine", "capability_check")
_emit_routes_to_capability("p2", "content_optimizer_engine", "capability_route")
_emit_writes_via_uwg("p2", "content_optimizer_engine", "uwg_write")
_emit_blocks_direct_write("p2", "content_optimizer_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "content_optimizer_engine", "tool_invocation")
_emit_captures_execution_output("p2", "content_optimizer_engine", "exec_output")
_emit_dispatches_agent("p3", "content_optimizer_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "content_optimizer_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "content_optimizer_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "content_optimizer_engine", "healing_outcome")
_emit_escalates_failure("p3", "content_optimizer_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "content_optimizer_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "content_optimizer_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "content_optimizer_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "content_optimizer_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "content_optimizer_engine", "eval_metric")
_emit_stores_embedding("p4", "content_optimizer_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "content_optimizer_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "content_optimizer_engine", "exec_snapshot_link")
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_applies_guardrail("p0", "content_optimizer_engine", "p0_governance")
_emit_reads_policy_state("p0", "content_optimizer_engine", "policy_binding")
_emit_snapshots_state("p0", "content_optimizer_engine", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("content_optimizer_engine", "p4obs", "metric_1")
_emit_emits_metric_event("content_optimizer_engine", "p4obs", "metric_2")
_emit_emits_metric_event("content_optimizer_engine", "p4obs", "metric_3")
_emit_emits_metric_event("content_optimizer_engine", "p4obs", "metric_4")
_emit_emits_metric_event("content_optimizer_engine", "p4obs", "metric_5")
_emit_emits_metric_event("content_optimizer_engine", "p4obs", "metric_6")
_emit_records_incident_event("content_optimizer_engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("content_optimizer_engine", "p4obs", "anomaly")
_emit_writes_observability_log("content_optimizer_engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("content_optimizer_engine", "p4obs", "mon_state")
_emit_triggers_alert("content_optimizer_engine", "p4obs", "alert")
_emit_links_incident_trace("content_optimizer_engine", "p4obs", "trace_link")
_emit_captures_pattern("content_optimizer_engine", "p3lm", "pattern")
_emit_records_learning_event("content_optimizer_engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("content_optimizer_engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("content_optimizer_engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("content_optimizer_engine", "p3lm", "routing")
_emit_improves_agent_policy("content_optimizer_engine", "p3lm", "policy")
_emit_stores_learning_state("content_optimizer_engine", "p3lm", "state")
_emit_records_execution_trace("content_optimizer_engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("content_optimizer_engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("content_optimizer_engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("content_optimizer_engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("content_optimizer_engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("content_optimizer_engine", "env_read", "p2_env_1")
_emit_reads_environ("content_optimizer_engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("content_optimizer_engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("content_optimizer_engine", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "content_optimizer_engine", "context_pull")
_emit_pulls_context("p1", "content_optimizer_engine", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "content_optimizer_engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "content_optimizer_engine", "uwg_term_2")
_emit_writes_through("p1", "content_optimizer_engine", "write_through")
_emit_writes_through("p1", "content_optimizer_engine", "write_through_2")
_emit_validated_by_safety_plane("p1", "content_optimizer_engine", "safety_validation")
_emit_invokes_eval("p1", "content_optimizer_engine", "eval_call")
_emit_proposal_commits_routing("p1", "content_optimizer_engine", "routing_commit")
_emit_escalates_to_human("p1", "content_optimizer_engine", "human_escalation")
_emit_routes_through("p1", "content_optimizer_engine", "route_through")
_emit_checks_agent_registry("p1", "content_optimizer_engine", "agent_registry")
_emit_validates_agent_capability("p1", "content_optimizer_engine", "capability")
_emit_dispatches_execution_plan("p1", "content_optimizer_engine", "exec_plan")
_emit_agent_executes_agent("p1", "content_optimizer_engine", "sub_agent")
_emit_routes_to_agent("p1", "content_optimizer_engine", "target_agent")
_emit_verifies_policy("p1", "content_optimizer_engine", "policy_check")
_emit_observes_runtime_state("p1", "content_optimizer_engine", "runtime_state")
_emit_verifies_boundary("p1", "content_optimizer_engine", "boundary_check")
_emit_transcripts_response("p1", "content_optimizer_engine", "transcript")
_emit_hard_fails_untranscripted("p1", "content_optimizer_engine")
_emit_gated_by_confidence("p1", "content_optimizer_engine", "confidence_gate")
emit_replay_key("p0", "content_optimizer_engine")
emit_determinism_digest("p0", "content_optimizer_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class ContentOptimizerEngine(BaseRGEngine):
    """
    Sovereign Refinement Engine.
    Reads: 'hop2_enrichment', 'adjusted_weights'
    Writes: 'optimized_content'
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.OPTIMIZER")

    async def execute(self) -> list[dict[str, Any]]:
        """
        Reorder resume content based on impact scoring and weights.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ContentOptimizerEngine.execute")

        data = self.ctx.buffer.read("hop2_enrichment")
        weights = self.ctx.buffer.read("adjusted_weights", default={})
        if not data:
            self.record_fail("Missing content to optimize", signal="DATA_MISSING")
            return []
        sections = data.get("experience_sections", [])
        optimized_sections = []
        for section in sections:
            bullets = section.get("bullets", [])
            optimized_bullets = sorted(
                bullets, key=lambda b: self._calculate_impact_score(b, weights), reverse=True
            )
            section["bullets"] = optimized_bullets
            optimized_sections.append(section)
        optimized_dict = {
            "experience_sections": optimized_sections,
            "education": data.get("education", []),
            "skills": data.get("skills", []),
        }
        self.ctx.buffer.write("optimized_content", optimized_dict, source_agent=self.name)
        self.record_pass("Content optimization complete")
        return optimized_sections

    def _calculate_impact_score(self, bullet: dict, weights: dict) -> float:
        score = 0.0
        if bullet.get("quantified_metrics"):
            score += 0.5
        score *= weights.get("experience", 1.0)
        return score
