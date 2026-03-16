"""
Writing Quality Engine - Tone/Voice check
Refactored from evaluate_writing_quality.py
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

_emit_applies_guardrail("p0", "writing_quality_engine", "p0_governance")
_emit_reads_policy_state("p0", "writing_quality_engine", "policy_binding")
_emit_snapshots_state("p0", "writing_quality_engine", "state_snapshot")
emit_replay_key("p0", "writing_quality_engine")
emit_determinism_digest("p0", "writing_quality_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class WritingQualityEngine(BaseRGEngine):
    """
    Evaluates writing quality, tone, and voice.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="QUALITY.WRITING")

    async def execute(self, text: str) -> dict[str, Any]:
        """
        Evaluate writing quality.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "WritingQualityEngine.execute")

        self._mcp_audit("writing_quality_check")
        issues = []
        score = 1.0
        if any(word in text.lower() for word in ["basically", "just", "simply"]):
            issues.append("Contains filler words")
            score -= 0.1
        if " I " in text or text.startswith("I "):
            issues.append("First-person voice detected")
            score -= 0.2
        passive_indicators = ["was managed", "were led", "is handled"]
        if any(indicator in text.lower() for indicator in passive_indicators):
            issues.append("Passive voice detected")
            score -= 0.15
        result = {"writing_score": max(score, 0.0), "issues": issues, "passed": score >= 0.7}
        if not result["passed"]:
            self.record_fail("Writing quality below threshold", data=result)
        else:
            self.record_pass("Writing quality validated")
        return result
