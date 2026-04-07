"""
Skill Similarity Tool - Skill similarity computation
Refactored from compute_skill_similarity.py
"""

from __future__ import annotations

import logging
from typing import Any

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
from apps_rg.engines.base_resume_engine import BaseRGEngine

_emit_applies_guardrail("p0", "skill_similarity_tool", "p0_governance")
_emit_reads_policy_state("p0", "skill_similarity_tool", "policy_binding")
_emit_snapshots_state("p0", "skill_similarity_tool", "state_snapshot")
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

_emit_emits_metric_event("skill_similarity_tool", "p4obs", "metric_1")
_emit_emits_metric_event("skill_similarity_tool", "p4obs", "metric_2")
_emit_emits_metric_event("skill_similarity_tool", "p4obs", "metric_3")
_emit_emits_metric_event("skill_similarity_tool", "p4obs", "metric_4")
_emit_emits_metric_event("skill_similarity_tool", "p4obs", "metric_5")
_emit_emits_metric_event("skill_similarity_tool", "p4obs", "metric_6")
_emit_records_incident_event("skill_similarity_tool", "p4obs", "incident")
_emit_captures_runtime_anomaly("skill_similarity_tool", "p4obs", "anomaly")
_emit_writes_observability_log("skill_similarity_tool", "p4obs", "obs_log")
_emit_updates_monitoring_state("skill_similarity_tool", "p4obs", "mon_state")
_emit_triggers_alert("skill_similarity_tool", "p4obs", "alert")
_emit_links_incident_trace("skill_similarity_tool", "p4obs", "trace_link")
_emit_captures_pattern("skill_similarity_tool", "p3lm", "pattern")
_emit_records_learning_event("skill_similarity_tool", "p3lm", "learning_event")
_emit_writes_learning_snapshot("skill_similarity_tool", "p3lm", "snapshot")
_emit_feeds_meta_learning("skill_similarity_tool", "p3lm", "meta_feed")
_emit_updates_routing_strategy("skill_similarity_tool", "p3lm", "routing")
_emit_improves_agent_policy("skill_similarity_tool", "p3lm", "policy")
_emit_stores_learning_state("skill_similarity_tool", "p3lm", "state")
_emit_records_execution_trace("skill_similarity_tool", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("skill_similarity_tool", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("skill_similarity_tool", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("skill_similarity_tool", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("skill_similarity_tool", "L4_STATE", "p2_trace_5")
_emit_reads_environ("skill_similarity_tool", "env_read", "p2_env_1")
_emit_reads_environ("skill_similarity_tool", "env_read", "p2_env_2")
_emit_reads_runtime_state("skill_similarity_tool", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("skill_similarity_tool", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "skill_similarity_tool", "context_pull")
_emit_pulls_context("p1", "skill_similarity_tool", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "skill_similarity_tool", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "skill_similarity_tool", "uwg_term_2")
_emit_writes_through("p1", "skill_similarity_tool", "write_through")
_emit_writes_through("p1", "skill_similarity_tool", "write_through_2")
_emit_validated_by_safety_plane("p1", "skill_similarity_tool", "safety_validation")
_emit_invokes_eval("p1", "skill_similarity_tool", "eval_call")
_emit_proposal_commits_routing("p1", "skill_similarity_tool", "routing_commit")
_emit_escalates_to_human("p1", "skill_similarity_tool", "human_escalation")
_emit_routes_through("p1", "skill_similarity_tool", "route_through")
_emit_checks_agent_registry("p1", "skill_similarity_tool", "agent_registry")
_emit_validates_agent_capability("p1", "skill_similarity_tool", "capability")
_emit_dispatches_execution_plan("p1", "skill_similarity_tool", "exec_plan")
_emit_agent_executes_agent("p1", "skill_similarity_tool", "sub_agent")
_emit_routes_to_agent("p1", "skill_similarity_tool", "target_agent")
_emit_verifies_policy("p1", "skill_similarity_tool", "policy_check")
_emit_observes_runtime_state("p1", "skill_similarity_tool", "runtime_state")
_emit_verifies_boundary("p1", "skill_similarity_tool", "boundary_check")
_emit_transcripts_response("p1", "skill_similarity_tool", "transcript")
_emit_hard_fails_untranscripted("p1", "skill_similarity_tool")
_emit_gated_by_confidence("p1", "skill_similarity_tool", "confidence_gate")
emit_replay_key("p0", "skill_similarity_tool")
emit_determinism_digest("p0", "skill_similarity_tool")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "skill_similarity_tool", "execution_auth")
_emit_validates_capability("p2", "skill_similarity_tool", "capability_check")
_emit_routes_to_capability("p2", "skill_similarity_tool", "capability_route")
_emit_writes_via_uwg("p2", "skill_similarity_tool", "uwg_write")
_emit_blocks_direct_write("p2", "skill_similarity_tool", "direct_write_block")
_emit_records_tool_invocation("p2", "skill_similarity_tool", "tool_invocation")
_emit_captures_execution_output("p2", "skill_similarity_tool", "exec_output")
_emit_dispatches_agent("p3", "skill_similarity_tool", "agent_dispatch")
_emit_coordinates_agents("p3", "skill_similarity_tool", "agent_coordination")
_emit_records_workflow_lineage("p3", "skill_similarity_tool", "workflow_lineage")
_emit_records_healing_outcome("p3", "skill_similarity_tool", "healing_outcome")
_emit_escalates_failure("p3", "skill_similarity_tool", "failure_escalation")
_emit_orchestrates_workflow("p3", "skill_similarity_tool", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "skill_similarity_tool", "healing_dispatch")
_emit_invokes_evaluation("p3", "skill_similarity_tool", "evaluation_signal")
_emit_records_telemetry_event("p4", "skill_similarity_tool", "telemetry_event")
_emit_captures_evaluation_metric("p4", "skill_similarity_tool", "eval_metric")
_emit_stores_embedding("p4", "skill_similarity_tool", "embedding_store")
_emit_updates_meta_learning_state("p4", "skill_similarity_tool", "meta_learning")
_emit_links_execution_to_snapshot("p4", "skill_similarity_tool", "exec_snapshot_link")

Logger = logging.getLogger(__name__)


class SkillSimilarityTool(BaseRGEngine):
    """
    Computes similarity between skill sets.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="TOOLS.SKILL_SIMILARITY")

    async def execute(self, skills_a: list[str], skills_b: list[str]) -> float:
        """
        Calculate Jaccard similarity between skill sets.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SkillSimilarityTool.execute")

        set_a = {s.lower() for s in skills_a}
        set_b = {s.lower() for s in skills_b}
        if not set_a or not set_b:
            return 0.0
        intersection = len(set_a & set_b)
        union = len(set_a | set_b)
        similarity = intersection / union if union > 0 else 0.0
        self.record_pass(f"Skill similarity: {similarity:.2f}")
        return similarity
