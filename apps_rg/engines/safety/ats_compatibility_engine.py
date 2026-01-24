"""
ATS Compatibility Engine - Ensures content is parseable by ATS systems
Refactored from ATSCompatibilityAgent.py
Following Batch 6 specifications
"""

from __future__ import annotations
from typing import Any, Dict, List
import logging
import re
import json

from apps_rg.engines.base.base_resume_engine import BaseRGEngine

Logger = logging.getLogger(__name__)


class ATSCompatibilityEngine(BaseRGEngine):
    """
    Sovereign Safety Engine.
    Ensures content is parseable by legacy Applicant Tracking Systems.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="SAFETY.ATS")
        # Patterns loaded from Knowledge Base or fallback to strict defaults
        self.forbidden_patterns = [
            (r"<table", "HTML Table Detected"),
            (r"<img", "Image Tag Detected"),
            (r"[│┃┆┇┊┋]", "Box Drawing Characters"),
            (r"[★☆●○◆◇■□▪▫]", "Non-Standard Bullet Points")
        ]

    async def execute(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Scan resume structure and content for parsing hazards.
        """
        self._mcp_audit("ats_scan_start")
        
        issues = []
        
        # 1. Serialize to string for regex scanning
        # (Efficient way to catch artifacts anywhere in the JSON)
        resume_str = json.dumps(resume_data)
        
        # 2. Pattern Matching
        for pattern, reason in self.forbidden_patterns:
            if re.search(pattern, resume_str):
                issues.append(reason)

        # 3. Structure Check
        # ATS systems require standard keys (Summary, Experience, Education)
        required_sections = ["experience", "education"]  # Minimal set
        missing = [k for k in required_sections if k not in resume_data]
        if missing:
            issues.append(f"Missing Standard Sections: {', '.join(missing)}")

        # 4. Result Recording
        if issues:
            self.record_fail(
                f"ATS Compatibility Failed: {len(issues)} issues", 
                data={"issues": issues},
                signal="ATS_FAILURE"  # Triggers Refinement Engine to adjust weights
            )
            return {
                "compatible": False,
                "issues": issues
            }

        self.record_pass("ATS Compatibility Verified")
        return {
            "compatible": True, 
            "issues": []
        }
