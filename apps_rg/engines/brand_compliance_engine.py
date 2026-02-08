"""
Brand Compliance Engine - Tone policing
Refactored from BrandComplianceAgent.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.BaseRGEngine import BaseRGEngine

Logger = logging.getLogger(__name__)


class BrandComplianceEngine(BaseRGEngine):
    """
    Enforces brand compliance and tone standards.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="SAFETY.BRAND")

    async def execute(self, content: dict[str, Any]) -> dict[str, Any]:
        """
        Validate brand compliance.
        """
        self._mcp_audit("brand_compliance_check")

        violations = []

        # Check for forbidden phrases
        forbidden_phrases = ["responsible for", "duties included", "helped with", "assisted in"]

        for section_name, section_content in content.items():
            text = str(section_content).lower()

            for phrase in forbidden_phrases:
                if phrase in text:
                    violations.append({"section": section_name, "phrase": phrase, "severity": "high"})

        result = {
            "compliant": len(violations) == 0,
            "violations": violations,
            "violation_count": len(violations),
        }

        if violations:
            self.record_fail(
                f"Brand compliance violations: {len(violations)}",
                data=result,
                signal="BRAND_VIOLATION",
            )
        else:
            self.record_pass("Brand compliance validated")

        return result
