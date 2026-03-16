"""
Quality Inspector Engine - Deep inspection
Refactored from InspectResumeQuality.py
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_applies_guardrail("p0", "quality_inspector_engine", "p0_governance")
_emit_reads_policy_state("p0", "quality_inspector_engine", "policy_binding")
_emit_snapshots_state("p0", "quality_inspector_engine", "state_snapshot")
emit_replay_key("p0", "quality_inspector_engine")
emit_determinism_digest("p0", "quality_inspector_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class QualityInspectorEngine(BaseRGEngine):
    """
    Deep quality inspection engine.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="QUALITY.INSPECTOR")

    async def execute(self, resume_data: dict[str, Any]) -> dict[str, Any]:
        """
        Perform deep quality inspection.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "QualityInspectorEngine.execute")

        self._mcp_audit("inspection_start")
        inspection_results = {
            "grammar_issues": [],
            "formatting_issues": [],
            "content_issues": [],
            "overall_quality": "pass",
        }
        for section in resume_data.values():
            text = str(section)
            if "  " in text:
                inspection_results["formatting_issues"].append("Double spaces detected")
            if text and text[0].islower():
                inspection_results["formatting_issues"].append("Section starts with lowercase")
        total_issues = (
            len(inspection_results["grammar_issues"])
            + len(inspection_results["formatting_issues"])
            + len(inspection_results["content_issues"])
        )
        if total_issues > 5:
            inspection_results["overall_quality"] = "fail"
            self.record_fail(f"Quality inspection failed: {total_issues} issues", data=inspection_results)
        else:
            self.record_pass(f"Quality inspection passed: {total_issues} minor issues")
        return inspection_results
