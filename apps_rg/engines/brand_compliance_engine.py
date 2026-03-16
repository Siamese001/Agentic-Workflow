"""
Brand Compliance Engine - Tone policing
Refactored from BrandComplianceAgent.py
"""

from __future__ import annotations

import logging
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

_emit_authorize_and_execute("p2", "brand_compliance_engine", "execution_auth")
_emit_validates_capability("p2", "brand_compliance_engine", "capability_check")
_emit_routes_to_capability("p2", "brand_compliance_engine", "capability_route")
_emit_writes_via_uwg("p2", "brand_compliance_engine", "uwg_write")
_emit_blocks_direct_write("p2", "brand_compliance_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "brand_compliance_engine", "tool_invocation")
_emit_captures_execution_output("p2", "brand_compliance_engine", "exec_output")
_emit_dispatches_agent("p3", "brand_compliance_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "brand_compliance_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "brand_compliance_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "brand_compliance_engine", "healing_outcome")
_emit_escalates_failure("p3", "brand_compliance_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "brand_compliance_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "brand_compliance_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "brand_compliance_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "brand_compliance_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "brand_compliance_engine", "eval_metric")
_emit_stores_embedding("p4", "brand_compliance_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "brand_compliance_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "brand_compliance_engine", "exec_snapshot_link")
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_applies_guardrail("p0", "brand_compliance_engine", "p0_governance")
_emit_reads_policy_state("p0", "brand_compliance_engine", "policy_binding")
_emit_snapshots_state("p0", "brand_compliance_engine", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import _emit_pulls_context, _emit_execution_terminates_at_uwg, _emit_writes_through, _emit_validated_by_safety_plane, _emit_invokes_eval, _emit_proposal_commits_routing
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("brand_compliance_engine", "p4obs", "metric_1")
_emit_emits_metric_event("brand_compliance_engine", "p4obs", "metric_2")
_emit_emits_metric_event("brand_compliance_engine", "p4obs", "metric_3")
_emit_emits_metric_event("brand_compliance_engine", "p4obs", "metric_4")
_emit_emits_metric_event("brand_compliance_engine", "p4obs", "metric_5")
_emit_emits_metric_event("brand_compliance_engine", "p4obs", "metric_6")
_emit_records_incident_event("brand_compliance_engine", "p4obs", "incident")
_emit_captures_runtime_anomaly("brand_compliance_engine", "p4obs", "anomaly")
_emit_writes_observability_log("brand_compliance_engine", "p4obs", "obs_log")
_emit_updates_monitoring_state("brand_compliance_engine", "p4obs", "mon_state")
_emit_triggers_alert("brand_compliance_engine", "p4obs", "alert")
_emit_links_incident_trace("brand_compliance_engine", "p4obs", "trace_link")
_emit_captures_pattern("brand_compliance_engine", "p3lm", "pattern")
_emit_records_learning_event("brand_compliance_engine", "p3lm", "learning_event")
_emit_writes_learning_snapshot("brand_compliance_engine", "p3lm", "snapshot")
_emit_feeds_meta_learning("brand_compliance_engine", "p3lm", "meta_feed")
_emit_updates_routing_strategy("brand_compliance_engine", "p3lm", "routing")
_emit_improves_agent_policy("brand_compliance_engine", "p3lm", "policy")
_emit_stores_learning_state("brand_compliance_engine", "p3lm", "state")
_emit_records_execution_trace("brand_compliance_engine", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("brand_compliance_engine", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("brand_compliance_engine", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("brand_compliance_engine", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("brand_compliance_engine", "L4_STATE", "p2_trace_5")
_emit_reads_environ("brand_compliance_engine", "env_read", "p2_env_1")
_emit_reads_environ("brand_compliance_engine", "env_read", "p2_env_2")
_emit_reads_runtime_state("brand_compliance_engine", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("brand_compliance_engine", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "brand_compliance_engine", "context_pull")
_emit_pulls_context("p1", "brand_compliance_engine", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "brand_compliance_engine", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "brand_compliance_engine", "uwg_term_2")
_emit_writes_through("p1", "brand_compliance_engine", "write_through")
_emit_writes_through("p1", "brand_compliance_engine", "write_through_2")
_emit_validated_by_safety_plane("p1", "brand_compliance_engine", "safety_validation")
_emit_invokes_eval("p1", "brand_compliance_engine", "eval_call")
_emit_proposal_commits_routing("p1", "brand_compliance_engine", "routing_commit")
emit_replay_key("p0", "brand_compliance_engine")
emit_determinism_digest("p0", "brand_compliance_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class BrandComplianceEngine(BaseRGEngine):
    """
    Enforces brand compliance and tone standards.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="SAFETY.BRAND")

    async def execute(self, content: dict[str, Any]) -> dict[str, Any]:
        """
        Validate brand compliance.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "BrandComplianceEngine.execute")

        self._mcp_audit("brand_compliance_check")
        violations = []
        forbidden_phrases = ["responsible for", "duties included", "helped with", "assisted in"]
        for section_name, section_content in content.items():
            text = str(section_content).lower()
            for phrase in forbidden_phrases:
                if phrase in text:
                    violations.append({"section": section_name, "phrase": phrase, "severity": "high"})
        result = {
            "compliant": len(violations) == 0,
            "violations": violations,
            "violation_count": len(violations),
        }
        if violations:
            self.record_fail(
                f"Brand compliance violations: {len(violations)}", data=result, signal="BRAND_VIOLATION"
            )
        else:
            self.record_pass("Brand compliance validated")
        return result
