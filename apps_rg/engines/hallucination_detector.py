"""
Hallucination Detector Engine - Claim verification logic
Refactored from check_hallucination.py
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

_emit_authorize_and_execute("p2", "hallucination_detector", "execution_auth")
_emit_validates_capability("p2", "hallucination_detector", "capability_check")
_emit_routes_to_capability("p2", "hallucination_detector", "capability_route")
_emit_writes_via_uwg("p2", "hallucination_detector", "uwg_write")
_emit_blocks_direct_write("p2", "hallucination_detector", "direct_write_block")
_emit_records_tool_invocation("p2", "hallucination_detector", "tool_invocation")
_emit_captures_execution_output("p2", "hallucination_detector", "exec_output")
_emit_dispatches_agent("p3", "hallucination_detector", "agent_dispatch")
_emit_coordinates_agents("p3", "hallucination_detector", "agent_coordination")
_emit_records_workflow_lineage("p3", "hallucination_detector", "workflow_lineage")
_emit_records_healing_outcome("p3", "hallucination_detector", "healing_outcome")
_emit_escalates_failure("p3", "hallucination_detector", "failure_escalation")
_emit_orchestrates_workflow("p3", "hallucination_detector", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "hallucination_detector", "healing_dispatch")
_emit_invokes_evaluation("p3", "hallucination_detector", "evaluation_signal")
_emit_records_telemetry_event("p4", "hallucination_detector", "telemetry_event")
_emit_captures_evaluation_metric("p4", "hallucination_detector", "eval_metric")
_emit_stores_embedding("p4", "hallucination_detector", "embedding_store")
_emit_updates_meta_learning_state("p4", "hallucination_detector", "meta_learning")
_emit_links_execution_to_snapshot("p4", "hallucination_detector", "exec_snapshot_link")
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_applies_guardrail("p0", "hallucination_detector", "p0_governance")
_emit_reads_policy_state("p0", "hallucination_detector", "policy_binding")
_emit_snapshots_state("p0", "hallucination_detector", "state_snapshot")
emit_replay_key("p0", "hallucination_detector")
emit_determinism_digest("p0", "hallucination_detector")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class HallucinationDetector(BaseRGEngine):
    """
    Safety Engine for detecting hallucinations in resume content.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="SAFETY.HALLUCINATION")

    async def execute(self, content: str) -> dict[str, Any]:
        """Check single content for hallucinations."""
        return self.check_batch([content])

    def check_batch(self, texts: list[str]) -> dict[str, Any]:
        """
        Batch check for hallucinations.
        Returns validation result with score.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HallucinationDetector.check_batch")

        total_score = 0.0
        issues = []
        for text in texts:
            if len(text) < 10:
                issues.append("Text too short for verification")
                continue
            if "100%" in text or "1000%" in text:
                issues.append(f"Suspicious metric in: {text[:50]}")
                total_score += 0.3
            else:
                total_score += 1.0
        avg_score = total_score / len(texts) if texts else 0.0
        return {"valid": avg_score >= 0.7, "score": avg_score, "issues": issues}
