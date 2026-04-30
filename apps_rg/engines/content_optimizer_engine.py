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

_emit_engine_lifecycle("content_optimizer_engine")


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
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "ContentOptimizerEngine.execute"
        )

        data = self.ctx.buffer.read("hop2_enrichment")
        weights = self.ctx.buffer.read("adjusted_weights", default={})
        if not data:
            self.record_fail("Missing content to optimize", signal="DATA_MISSING")
            return []
        sections = data.get("experience_sections", [])
        optimized_sections = []
        # Per-section retention threshold. If a bullet's alignment_score falls
        # below this AND the section has more bullets than `min_bullets_per_section`,
        # drop it. This is the JD-customization gate — bullets that don't talk
        # about what the JD is asking for don't ship.
        min_bullets_per_section = 3
        max_bullets_per_section = 6
        retention_threshold = 0.18  # bullets below this are dropped if section has slack
        for section in sections:
            bullets = section.get("bullets", [])
            scored = sorted(
                bullets,
                key=lambda b: self._calculate_impact_score(b, weights),
                reverse=True,
            )
            # Apply retention threshold: keep top N, drop the tail below threshold
            # but always keep at least `min_bullets_per_section`.
            keep = []
            for idx, bullet in enumerate(scored):
                align = float(bullet.get("alignment_score", 0.0))
                if idx < min_bullets_per_section:
                    keep.append(bullet)
                elif idx < max_bullets_per_section and align >= retention_threshold:
                    keep.append(bullet)
            section["bullets"] = keep
            optimized_sections.append(section)
        optimized_dict = {
            "experience_sections": optimized_sections,
            "education": data.get("education", []),
            "skills": data.get("skills", []),
        }
        self.ctx.buffer.write("optimized_content", optimized_dict, source_agent=self.name)
        n_kept = sum(len(s.get("bullets", [])) for s in optimized_sections)
        self.record_pass(f"Content optimization complete — kept {n_kept} bullets across {len(optimized_sections)} sections")
        return optimized_sections

    def _calculate_impact_score(self, bullet: dict, weights: dict) -> float:
        """Composite score = JD-alignment + quantification + section weight.

        JD alignment dominates: a high-quantification bullet that doesn't speak
        to the JD ranks below a JD-aligned bullet without metrics. This is the
        actual customization signal the pipeline was missing.
        """
        align = float(bullet.get("alignment_score", 0.0))
        score = 0.7 * align
        if bullet.get("quantified_metrics"):
            score += 0.2
        score *= weights.get("experience", 1.0)
        return score
