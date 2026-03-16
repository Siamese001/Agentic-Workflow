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
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)
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
