"""
Quality Inspector Engine - Deep inspection
Refactored from InspectResumeQuality.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.BaseRGEngine import BaseRGEngine

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
        self._mcp_audit("inspection_start")

        inspection_results = {
            "grammar_issues": [],
            "formatting_issues": [],
            "content_issues": [],
            "overall_quality": "pass",
        }

        # Check grammar patterns
        for section in resume_data.values():
            text = str(section)

            # Check for double spaces
            if "  " in text:
                inspection_results["formatting_issues"].append("Double spaces detected")

            # Check for inconsistent capitalization
            if text and text[0].islower():
                inspection_results["formatting_issues"].append("Section starts with lowercase")

        # Determine overall quality
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
