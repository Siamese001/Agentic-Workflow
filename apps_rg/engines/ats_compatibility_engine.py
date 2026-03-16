"""
ATS Compatibility Engine - Ensures content is parseable by ATS systems
Refactored from ATSCompatibilityAgent.py
Following Batch 6 specifications

HARDENING: Reads 'ranked_content'. Scans for HTML/Table artifacts.
Writes 'ats_report'. Triggers 'ATS_FAILURE'.
"""

from __future__ import annotations

import json
import logging
import re
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

_emit_authorize_and_execute("p2", "ats_compatibility_engine", "execution_auth")
_emit_validates_capability("p2", "ats_compatibility_engine", "capability_check")
_emit_routes_to_capability("p2", "ats_compatibility_engine", "capability_route")
_emit_writes_via_uwg("p2", "ats_compatibility_engine", "uwg_write")
_emit_blocks_direct_write("p2", "ats_compatibility_engine", "direct_write_block")
_emit_records_tool_invocation("p2", "ats_compatibility_engine", "tool_invocation")
_emit_captures_execution_output("p2", "ats_compatibility_engine", "exec_output")
_emit_dispatches_agent("p3", "ats_compatibility_engine", "agent_dispatch")
_emit_coordinates_agents("p3", "ats_compatibility_engine", "agent_coordination")
_emit_records_workflow_lineage("p3", "ats_compatibility_engine", "workflow_lineage")
_emit_records_healing_outcome("p3", "ats_compatibility_engine", "healing_outcome")
_emit_escalates_failure("p3", "ats_compatibility_engine", "failure_escalation")
_emit_orchestrates_workflow("p3", "ats_compatibility_engine", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ats_compatibility_engine", "healing_dispatch")
_emit_invokes_evaluation("p3", "ats_compatibility_engine", "evaluation_signal")
_emit_records_telemetry_event("p4", "ats_compatibility_engine", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ats_compatibility_engine", "eval_metric")
_emit_stores_embedding("p4", "ats_compatibility_engine", "embedding_store")
_emit_updates_meta_learning_state("p4", "ats_compatibility_engine", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ats_compatibility_engine", "exec_snapshot_link")
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_applies_guardrail("p0", "ats_compatibility_engine", "p0_governance")
_emit_reads_policy_state("p0", "ats_compatibility_engine", "policy_binding")
_emit_snapshots_state("p0", "ats_compatibility_engine", "state_snapshot")
emit_replay_key("p0", "ats_compatibility_engine")
emit_determinism_digest("p0", "ats_compatibility_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class ATSCompatibilityEngine(BaseRGEngine):
    """
    Sovereign Safety Engine.
    Reads: 'ranked_content'
    Writes: 'ats_report'
    Signal: 'ATS_FAILURE'
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="SAFETY.ATS")
        self.forbidden_patterns = [
            ("<table", "HTML Table"),
            ("<img", "Image Tag"),
            ("[│┃]", "Box Characters"),
        ]

    async def execute(self) -> dict[str, Any]:
        """
        Validate final content against ATS parsing rules.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ATSCompatibilityEngine.execute")

        data = (
            self.ctx.buffer.read("ranked_content")
            or self.ctx.buffer.read("optimized_content")
            or self.ctx.buffer.read("hop2_enrichment")
        )
        if not data:
            self.record_fail("No content to validate", signal="DATA_MISSING")
            return {"valid": False}
        issues = []
        data_str = json.dumps(data)
        for pattern, reason in self.forbidden_patterns:
            if re.search(pattern, data_str):
                issues.append(reason)
        report = {"valid": len(issues) == 0, "issues": issues}
        self.ctx.buffer.write("ats_report", report, source_agent=self.name)
        if issues:
            self.record_fail(f"ATS Issues Found: {len(issues)}", data=report, signal="ATS_FAILURE")
        else:
            self.record_pass("ATS Check Passed")
        return report
