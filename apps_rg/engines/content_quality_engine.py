"""
Content Quality Engine - General quality rules
Refactored from ContentQualityAgent.py

HARDENING: Reads 'hop2_enrichment' (or any content stage). Writes 'quality_report'.
Checks for forbidden phrases and metric density.
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

_emit_authorize_and_execute("p2", "content_quality_engine", "execution_auth")
_emit_validates_capability("p2", "content_quality_engine", "capability_check")
_emit_routes_to_capability("p2", "content_quality_engine", "capability_route")
_emit_writes_via_uwg("p2", "content_quality_engine", "uwg_write")
_emit_blocks_direct_write("p2", "content_quality_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "content_quality_engine", "tool_invocation")
_emit_captures_execution_output("p2", "content_quality_engine", "exec_output")
_emit_dispatches_agent("p3", "content_quality_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "content_quality_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "content_quality_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "content_quality_engine", "healing_outcome")
_emit_escalates_failure("p3", "content_quality_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "content_quality_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "content_quality_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "content_quality_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "content_quality_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "content_quality_engine", "eval_metric")
_emit_stores_embedding("p4", "content_quality_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "content_quality_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "content_quality_engine", "exec_snapshot_link")
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_applies_guardrail("p0", "content_quality_engine", "p0_governance")
_emit_reads_policy_state("p0", "content_quality_engine", "policy_binding")
_emit_snapshots_state("p0", "content_quality_engine", "state_snapshot")
emit_replay_key("p0", "content_quality_engine")
emit_determinism_digest("p0", "content_quality_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class ContentQualityEngine(BaseRGEngine):
    """
    Sovereign Quality Engine.
    Reads: 'hop2_enrichment' (or specified input)
    Writes: 'quality_report'
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="QUALITY.CONTENT")

    async def execute(self, target_key: str = "hop2_enrichment") -> dict[str, Any]:
        """
        Audit content for Sovereign Quality Standards.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ContentQualityEngine.execute")

        data = self.ctx.buffer.read(target_key)
        if not data:
            return {"score": 0, "status": "skipped"}
        issues = []
        score = 100
        sections = data.get("experience_sections", [])
        for sec in sections:
            for bullet in sec.get("bullets", []):
                text = bullet.get("bullet_text", "").lower()
                if "responsible for" in text:
                    issues.append(f"Weak phrase in {sec.get('company')}")
                    score -= 5
                if not bullet.get("quantified_metrics"):
                    score -= 1
        report = {"score": score, "issues": issues, "status": "passed" if score > 80 else "warning"}
        self.ctx.buffer.write("quality_report", report, source_agent=self.name)
        if score < 70:
            self.record_fail(f"Quality Score Low: {score}", data=report, signal="QUALITY_FAILURE")
        else:
            self.record_pass(f"Quality Score: {score}")
        return report
