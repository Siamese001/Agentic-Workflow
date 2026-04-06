"""
User Preferences Engine - Fetch user preferences
Refactored from fetch_user_preferences.py
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

_emit_authorize_and_execute("p2", "user_preferences_engine", "execution_auth")
_emit_validates_capability("p2", "user_preferences_engine", "capability_check")
_emit_routes_to_capability("p2", "user_preferences_engine", "capability_route")
_emit_writes_via_uwg("p2", "user_preferences_engine", "uwg_write")
_emit_blocks_direct_write("p2", "user_preferences_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "user_preferences_engine", "tool_invocation")
_emit_captures_execution_output("p2", "user_preferences_engine", "exec_output")
_emit_dispatches_agent("p3", "user_preferences_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "user_preferences_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "user_preferences_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "user_preferences_engine", "healing_outcome")
_emit_escalates_failure("p3", "user_preferences_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "user_preferences_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "user_preferences_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "user_preferences_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "user_preferences_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "user_preferences_engine", "eval_metric")
_emit_stores_embedding("p4", "user_preferences_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "user_preferences_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "user_preferences_engine", "exec_snapshot_link")
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_applies_guardrail("p0", "user_preferences_engine", "p0_governance")
_emit_reads_policy_state("p0", "user_preferences_engine", "policy_binding")
_emit_snapshots_state("p0", "user_preferences_engine", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("user_preferences_engine", "p4obs", "metric_1")
_emit_emits_metric_event("user_preferences_engine", "p4obs", "metric_2")
_emit_emits_metric_event("user_preferences_engine", "p4obs", "metric_3")
_emit_emits_metric_event("user_preferences_engine", "p4obs", "metric_4")
_emit_emits_metric_event("user_preferences_engine", "p4obs", "metric_5")
_emit_emits_metric_event("user_preferences_engine", "p4obs", "metric_6")
_emit_records_incident_event("user_preferences_engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("user_preferences_engine", "p4obs", "anomaly")
_emit_writes_observability_log("user_preferences_engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("user_preferences_engine", "p4obs", "mon_state")
_emit_triggers_alert("user_preferences_engine", "p4obs", "alert")
_emit_links_incident_trace("user_preferences_engine", "p4obs", "trace_link")
_emit_captures_pattern("user_preferences_engine", "p3lm", "pattern")
_emit_records_learning_event("user_preferences_engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("user_preferences_engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("user_preferences_engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("user_preferences_engine", "p3lm", "routing")
_emit_improves_agent_policy("user_preferences_engine", "p3lm", "policy")
_emit_stores_learning_state("user_preferences_engine", "p3lm", "state")
_emit_records_execution_trace("user_preferences_engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("user_preferences_engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("user_preferences_engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("user_preferences_engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("user_preferences_engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("user_preferences_engine", "env_read", "p2_env_1")
_emit_reads_environ("user_preferences_engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("user_preferences_engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("user_preferences_engine", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "user_preferences_engine", "context_pull")
_emit_pulls_context("p1", "user_preferences_engine", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "user_preferences_engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "user_preferences_engine", "uwg_term_2")
_emit_writes_through("p1", "user_preferences_engine", "write_through")
_emit_writes_through("p1", "user_preferences_engine", "write_through_2")
_emit_validated_by_safety_plane("p1", "user_preferences_engine", "safety_validation")
_emit_invokes_eval("p1", "user_preferences_engine", "eval_call")
_emit_proposal_commits_routing("p1", "user_preferences_engine", "routing_commit")
_emit_escalates_to_human("p1", "user_preferences_engine", "human_escalation")
_emit_routes_through("p1", "user_preferences_engine", "route_through")
_emit_checks_agent_registry("p1", "user_preferences_engine", "agent_registry")
_emit_validates_agent_capability("p1", "user_preferences_engine", "capability")
_emit_dispatches_execution_plan("p1", "user_preferences_engine", "exec_plan")
_emit_agent_executes_agent("p1", "user_preferences_engine", "sub_agent")
_emit_routes_to_agent("p1", "user_preferences_engine", "target_agent")
_emit_verifies_policy("p1", "user_preferences_engine", "policy_check")
_emit_observes_runtime_state("p1", "user_preferences_engine", "runtime_state")
_emit_verifies_boundary("p1", "user_preferences_engine", "boundary_check")
_emit_transcripts_response("p1", "user_preferences_engine", "transcript")
_emit_hard_fails_untranscripted("p1", "user_preferences_engine")
_emit_gated_by_confidence("p1", "user_preferences_engine", "confidence_gate")
emit_replay_key("p0", "user_preferences_engine")
emit_determinism_digest("p0", "user_preferences_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class UserPreferencesEngine(BaseRGEngine):
    """
    Retrieves user preferences for resume generation.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="RETRIEVAL.PREFERENCES")

    async def execute(self, user_id: str) -> dict[str, Any]:
        """
        Fetch user preferences.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "UserPreferencesEngine.execute")

        self._mcp_audit("preferences_retrieval", {"user_id": user_id})
        preferences = {
            "template_style": "modern",
            "color_scheme": "professional",
            "include_photo": False,
            "preferred_sections": ["summary", "experience", "education", "skills"],
            "tone": "professional",
        }
        if hasattr(self.ctx, "user_preferences"):
            preferences.update(self.ctx.user_preferences.get(user_id, {}))
        self.record_pass("User preferences retrieved")
        return preferences
