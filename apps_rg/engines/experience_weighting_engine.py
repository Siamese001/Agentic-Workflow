"""
Experience Weighting Engine - Experience relevance weighting
Refactored from weight_experience_match.py
"""

from __future__ import annotations

from agentic_core.runtime.contracts.runtime_telemetry_decorators import (
    traces_execute,
)

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

_emit_engine_lifecycle("experience_weighting_engine")


Logger = logging.getLogger(__name__)


class ExperienceWeightingEngine(BaseRGEngine):
    """
    Weights experience sections by relevance to target role.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="QUALITY.EXPERIENCE_WEIGHTING")

    @traces_execute(layer="L3_ORCHESTRATION")
    async def execute(self, experiences: list[dict[str, Any]], target_role: str) -> list[dict[str, Any]]:
        """
        Calculate relevance weights for experience sections.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ExperienceWeightingEngine.execute"
        )

        self._mcp_audit("experience_weighting")
        weighted_experiences = []
        for exp in experiences:
            weight = self._calculate_relevance(exp, target_role)
            exp["relevance_weight"] = weight
            weighted_experiences.append(exp)
        weighted_experiences.sort(key=lambda x: x["relevance_weight"], reverse=True)
        self.record_pass(f"Weighted {len(weighted_experiences)} experiences")
        return weighted_experiences

    def _calculate_relevance(self, experience: dict[str, Any], target_role: str) -> float:
        """Calculate relevance score."""
        score = 0.5
        title = experience.get("title", "").lower()
        target_lower = target_role.lower()
        if target_lower in title:
            score += 0.5
        related_keywords = ["senior", "lead", "principal", "staff"]
        if any(kw in title for kw in related_keywords):
            score += 0.2
        return min(score, 1.0)
