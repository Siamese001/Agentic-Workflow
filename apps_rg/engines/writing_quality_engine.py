"""
Writing Quality Engine - Tone/Voice check
Refactored from evaluate_writing_quality.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.base_rg_engine import BaseRGEngine
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

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
