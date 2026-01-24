"""
ATS Compatibility Engine - Ensures content is parseable by ATS systems
Refactored from ATSCompatibilityAgent.py
Following Batch 6 specifications

HARDENING: Reads 'ranked_content'. Scans for HTML/Table artifacts.
Writes 'ats_report'. Triggers 'ATS_FAILURE'.
"""

from __future__ import annotations
from typing import Any
import logging
import re
import json

from apps_rg.engines.base.base_resume_engine import BaseRGEngine

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
            (r"<table", "HTML Table"),
            (r"<img", "Image Tag"),
            (r"[│┃]", "Box Characters"),
        ]

    async def execute(self) -> dict[str, Any]:
        """
        Validate final content against ATS parsing rules.
        """
        # 1. READ
        # Check ranked first, then optimized, then enriched
        data = (
            self.ctx.buffer.read("ranked_content")
            or self.ctx.buffer.read("optimized_content")
            or self.ctx.buffer.read("hop2_enrichment")
        )

        if not data:
            self.record_fail("No content to validate", signal="DATA_MISSING")
            return {"valid": False}

        # 2. LOGIC
        issues = []
        data_str = json.dumps(data)

        for pattern, reason in self.forbidden_patterns:
            if re.search(pattern, data_str):
                issues.append(reason)

        # 3. WRITE
        report = {"valid": len(issues) == 0, "issues": issues}
        self.ctx.buffer.write("ats_report", report, source_agent=self.name)

        # 4. SIGNAL
        if issues:
            self.record_fail(f"ATS Issues Found: {len(issues)}", data=report, signal="ATS_FAILURE")
        else:
            self.record_pass("ATS Check Passed")

        return report
