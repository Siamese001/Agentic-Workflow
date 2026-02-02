"""
Generation Diagnostics Engine - Failure analysis
Refactored from diagnose_generation_issues.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.base.BaseRGEngine import BaseRGEngine

Logger = logging.getLogger(__name__)


class GenerationDiagnosticsEngine(BaseRGEngine):
    """
    Diagnoses generation failures and provides remediation suggestions.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="QUALITY.DIAGNOSTICS")

    async def execute(self, failure_context: dict[str, Any]) -> dict[str, Any]:
        """
        Diagnose generation failure and suggest fixes.
        """
        self._mcp_audit("diagnostics_start")

        diagnosis = {"root_cause": "unknown", "contributing_factors": [], "remediation_steps": []}

        # Analyze failure signals
        if failure_context.get("empty_output"):
            diagnosis["root_cause"] = "llm_timeout_or_budget"
            diagnosis["remediation_steps"].append("Increase timeout threshold")
            diagnosis["remediation_steps"].append("Simplify prompt")

        if failure_context.get("invalid_format"):
            diagnosis["root_cause"] = "parsing_failure"
            diagnosis["remediation_steps"].append("Add format constraints to prompt")

        if failure_context.get("quality_score", 1.0) < 0.5:
            diagnosis["root_cause"] = "insufficient_context"
            diagnosis["contributing_factors"].append("Low quality score")
            diagnosis["remediation_steps"].append("Enrich input context")

        self.record_pass("Diagnostics complete", data=diagnosis)
        return diagnosis
