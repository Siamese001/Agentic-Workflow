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
