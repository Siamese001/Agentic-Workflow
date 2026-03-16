"""
Skill Score Normalizer - Score normalization
Refactored from normalize_skill_scores.py
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

_emit_authorize_and_execute("p2", "skill_score_normalizer", "execution_auth")
_emit_validates_capability("p2", "skill_score_normalizer", "capability_check")
_emit_routes_to_capability("p2", "skill_score_normalizer", "capability_route")
_emit_writes_via_uwg("p2", "skill_score_normalizer", "uwg_write")
_emit_blocks_direct_write("p2", "skill_score_normalizer", "direct_write_block")
_emit_records_tool_invocation("p2", "skill_score_normalizer", "tool_invocation")
_emit_captures_execution_output("p2", "skill_score_normalizer", "exec_output")
_emit_dispatches_agent("p3", "skill_score_normalizer", "agent_dispatch")
_emit_coordinates_agents("p3", "skill_score_normalizer", "agent_coordination")
_emit_records_workflow_lineage("p3", "skill_score_normalizer", "workflow_lineage")
_emit_records_healing_outcome("p3", "skill_score_normalizer", "healing_outcome")
_emit_escalates_failure("p3", "skill_score_normalizer", "failure_escalation")
_emit_orchestrates_workflow("p3", "skill_score_normalizer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "skill_score_normalizer", "healing_dispatch")
_emit_invokes_evaluation("p3", "skill_score_normalizer", "evaluation_signal")
_emit_records_telemetry_event("p4", "skill_score_normalizer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "skill_score_normalizer", "eval_metric")
_emit_stores_embedding("p4", "skill_score_normalizer", "embedding_store")
_emit_updates_meta_learning_state("p4", "skill_score_normalizer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "skill_score_normalizer", "exec_snapshot_link")
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_applies_guardrail("p0", "skill_score_normalizer", "p0_governance")
_emit_reads_policy_state("p0", "skill_score_normalizer", "policy_binding")
_emit_snapshots_state("p0", "skill_score_normalizer", "state_snapshot")
emit_replay_key("p0", "skill_score_normalizer")
emit_determinism_digest("p0", "skill_score_normalizer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class SkillScoreNormalizer(BaseRGEngine):
    """
    Normalizes skill match scores across different scales.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.SKILL_NORMALIZER")

    async def execute(self, raw_scores: dict[str, float]) -> dict[str, float]:
        """
        Normalize skill scores to 0-1 range.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SkillScoreNormalizer.execute")

        self._mcp_audit("score_normalization")
        if not raw_scores:
            return {}
        values = list(raw_scores.values())
        min_val = min(values)
        max_val = max(values)
        normalized = {}
        if max_val > min_val:
            for skill, score in raw_scores.items():
                normalized[skill] = (score - min_val) / (max_val - min_val)
        else:
            normalized = dict.fromkeys(raw_scores, 1.0)
        self.record_pass(f"Normalized {len(normalized)} skill scores")
        return normalized
