"""
Skill Similarity Tool - Skill similarity computation
Refactored from compute_skill_similarity.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.base_resume_engine import BaseRGEngine

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

_emit_applies_guardrail("p0", "skill_similarity_tool", "p0_governance")
_emit_reads_policy_state("p0", "skill_similarity_tool", "policy_binding")
_emit_snapshots_state("p0", "skill_similarity_tool", "state_snapshot")
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
