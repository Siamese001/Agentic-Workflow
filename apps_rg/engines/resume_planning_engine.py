"""
Resume Planning Engine - L1 Planner
Refactored from resume_planner.py
Now delegates to logic_nodes for deterministic logic extraction.
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
from apps_rg.types.resume_section_node import ResumeSectionNode

from apps_rg.engines.base_rg_engine import BaseRGEngine

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

from apps_rg.engines._lifecycle_emits import _emit_engine_lifecycle

_emit_engine_lifecycle("resume_planning_engine")


Logger = logging.getLogger(__name__)


class ResumePlanningEngine(BaseRGEngine):
    """
    L1 Planning - Role/Industry focus determination.

    Now delegates role/industry extraction to ResumeSectionNode logic node
    to comply with Blueprint Depth-2 Structure requirements.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="ORCHESTRATION.PLANNING")
        self.section_node = ResumeSectionNode(config=self.config.get("section_config", {}))

    async def execute(self, job_description: str, candidate_profile: dict[str, Any]) -> dict[str, Any]:
        """
        Create initial resume generation plan using delegated logic nodes.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ResumePlanningEngine.execute"
        )

        self._mcp_audit("planning_start")
        section_analysis = self.section_node(job_description, candidate_profile)
        plan = {
            "target_role": section_analysis.role_result.role,
            "target_industry": section_analysis.industry_result.industry,
            "role_confidence": section_analysis.role_result.confidence,
            "industry_confidence": section_analysis.industry_result.confidence,
            "seniority_level": section_analysis.role_result.seniority_level,
            "required_sections": section_analysis.section_analysis.required_sections,
            "optional_sections": section_analysis.section_analysis.optional_sections,
            "emphasis_areas": section_analysis.section_analysis.emphasis_areas,
            "section_weights": section_analysis.section_analysis.section_weights,
            "k_nodes_required": ["K.1", "K.2", "K.3", "K.4", "K.5", "K.6", "K.7", "K.8", "K.9"],
        }
        if "leadership" in job_description.lower():
            plan["emphasis_areas"].append("K.9")
        if "technical" in job_description.lower() or "engineer" in job_description.lower():
            plan["emphasis_areas"].extend(["K.6", "K.7"])
        self.record_pass("Resume plan created using logic nodes", data=plan)
        return plan
