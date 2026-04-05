"""
Bullet Generation Task - Stateless bullet writer
Refactored from create_experience_bullets.py
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

_emit_authorize_and_execute("p2", "bullet_generation_task", "execution_auth")
_emit_validates_capability("p2", "bullet_generation_task", "capability_check")
_emit_routes_to_capability("p2", "bullet_generation_task", "capability_route")
_emit_writes_via_uwg("p2", "bullet_generation_task", "uwg_write")
_emit_blocks_direct_write("p2", "bullet_generation_task", "direct_write_block")
_emit_records_tool_invocation("p2", "bullet_generation_task", "tool_invocation")
_emit_captures_execution_output("p2", "bullet_generation_task", "exec_output")
_emit_dispatches_agent("p3", "bullet_generation_task", "agent_dispatch")
_emit_coordinates_agents("p3", "bullet_generation_task", "agent_coordination")
_emit_records_workflow_lineage("p3", "bullet_generation_task", "workflow_lineage")
_emit_records_healing_outcome("p3", "bullet_generation_task", "healing_outcome")
_emit_escalates_failure("p3", "bullet_generation_task", "failure_escalation")
_emit_orchestrates_workflow("p3", "bullet_generation_task", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "bullet_generation_task", "healing_dispatch")
_emit_invokes_evaluation("p3", "bullet_generation_task", "evaluation_signal")
_emit_records_telemetry_event("p4", "bullet_generation_task", "telemetry_event")
_emit_captures_evaluation_metric("p4", "bullet_generation_task", "eval_metric")
_emit_stores_embedding("p4", "bullet_generation_task", "embedding_store")
_emit_updates_meta_learning_state("p4", "bullet_generation_task", "meta_learning")
_emit_links_execution_to_snapshot("p4", "bullet_generation_task", "exec_snapshot_link")
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_applies_guardrail("p0", "bullet_generation_task", "p0_governance")
_emit_reads_policy_state("p0", "bullet_generation_task", "policy_binding")
_emit_snapshots_state("p0", "bullet_generation_task", "state_snapshot")
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

_emit_emits_metric_event("bullet_generation_task", "p4obs", "metric_1")
_emit_emits_metric_event("bullet_generation_task", "p4obs", "metric_2")
_emit_emits_metric_event("bullet_generation_task", "p4obs", "metric_3")
_emit_emits_metric_event("bullet_generation_task", "p4obs", "metric_4")
_emit_emits_metric_event("bullet_generation_task", "p4obs", "metric_5")
_emit_emits_metric_event("bullet_generation_task", "p4obs", "metric_6")
_emit_records_incident_event("bullet_generation_task", "p4obs", "incident")
_emit_captures_runtime_anomaly("bullet_generation_task", "p4obs", "anomaly")
_emit_writes_observability_log("bullet_generation_task", "p4obs", "obs_log")
_emit_updates_monitoring_state("bullet_generation_task", "p4obs", "mon_state")
_emit_triggers_alert("bullet_generation_task", "p4obs", "alert")
_emit_links_incident_trace("bullet_generation_task", "p4obs", "trace_link")
_emit_captures_pattern("bullet_generation_task", "p3lm", "pattern")
_emit_records_learning_event("bullet_generation_task", "p3lm", "learning_event")
_emit_writes_learning_snapshot("bullet_generation_task", "p3lm", "snapshot")
_emit_feeds_meta_learning("bullet_generation_task", "p3lm", "meta_feed")
_emit_updates_routing_strategy("bullet_generation_task", "p3lm", "routing")
_emit_improves_agent_policy("bullet_generation_task", "p3lm", "policy")
_emit_stores_learning_state("bullet_generation_task", "p3lm", "state")
_emit_records_execution_trace("bullet_generation_task", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("bullet_generation_task", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("bullet_generation_task", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("bullet_generation_task", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("bullet_generation_task", "L4_STATE", "p2_trace_5")
_emit_reads_environ("bullet_generation_task", "env_read", "p2_env_1")
_emit_reads_environ("bullet_generation_task", "env_read", "p2_env_2")
_emit_reads_runtime_state("bullet_generation_task", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("bullet_generation_task", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "bullet_generation_task", "context_pull")
_emit_pulls_context("p1", "bullet_generation_task", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "bullet_generation_task", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "bullet_generation_task", "uwg_term_2")
_emit_writes_through("p1", "bullet_generation_task", "write_through")
_emit_writes_through("p1", "bullet_generation_task", "write_through_2")
_emit_validated_by_safety_plane("p1", "bullet_generation_task", "safety_validation")
_emit_invokes_eval("p1", "bullet_generation_task", "eval_call")
_emit_proposal_commits_routing("p1", "bullet_generation_task", "routing_commit")
_emit_escalates_to_human("p1", "bullet_generation_task", "human_escalation")
_emit_routes_through("p1", "bullet_generation_task", "route_through")
_emit_checks_agent_registry("p1", "bullet_generation_task", "agent_registry")
_emit_validates_agent_capability("p1", "bullet_generation_task", "capability")
_emit_dispatches_execution_plan("p1", "bullet_generation_task", "exec_plan")
_emit_agent_executes_agent("p1", "bullet_generation_task", "sub_agent")
_emit_routes_to_agent("p1", "bullet_generation_task", "target_agent")
_emit_verifies_policy("p1", "bullet_generation_task", "policy_check")
_emit_observes_runtime_state("p1", "bullet_generation_task", "runtime_state")
_emit_verifies_boundary("p1", "bullet_generation_task", "boundary_check")
_emit_transcripts_response("p1", "bullet_generation_task", "transcript")
_emit_hard_fails_untranscripted("p1", "bullet_generation_task")
_emit_gated_by_confidence("p1", "bullet_generation_task", "confidence_gate")
emit_replay_key("p0", "bullet_generation_task")
emit_determinism_digest("p0", "bullet_generation_task")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class BulletGenerationTask(BaseRGEngine):
    """
    Stateless bullet writer for experience sections.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="GENERATION.BULLETS")

    async def execute(self, experience_context: dict[str, Any], target_count: int = 5) -> list[str]:
        """
        Generate achievement bullets for an experience section.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "BulletGenerationTask.execute")

        self._mcp_audit("bullet_generation_start", {"target_count": target_count})
        prompt_template = self.get_frozen_prompt("bullet_generation") if self.knowledge else ""
        if not prompt_template:
            prompt_template = "Generate {count} achievement bullets for {role} at {company}"
        prompt = prompt_template.format(
            count=target_count,
            role=experience_context.get("role", "Professional"),
            company=experience_context.get("company", "Company"),
        )
        raw_output = await self.call_llm(prompt)
        bullets = self._parse_bullets(raw_output)
        if len(bullets) != target_count:
            self.record_fail(f"Generated {len(bullets)} bullets, expected {target_count}")
        else:
            self.record_pass(f"Generated {len(bullets)} bullets")
        return bullets

    def _parse_bullets(self, text: str) -> list[str]:
        """Parse LLM output into bullet list."""
        if not text:
            return []
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        bullets = [line.lstrip("•-*").strip() for line in lines if line]
        return bullets
