"""
Content Quality Engine - General quality rules
Refactored from ContentQualityAgent.py
"""

from __future__ import annotations
from typing import Any
import logging

from apps_rg.engines.base.base_resume_engine import BaseRGEngine

Logger = logging.getLogger(__name__)


class ContentQualityEngine(BaseRGEngine):
    """
    General content quality validation.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="QUALITY.CONTENT")

    async def execute(self, content: dict[str, Any]) -> dict[str, Any]:
        """
        Validate content quality across multiple dimensions.
        """
        self._mcp_audit("quality_check_start")

        issues = []
        score = 1.0

        # Check for common quality issues
        for section_name, section_content in content.items():
            text = str(section_content)

            # Check for weak verbs
            weak_verbs = ["responsible for", "duties included", "helped with"]
            for verb in weak_verbs:
                if verb in text.lower():
                    issues.append(f"{section_name}: Contains weak verb '{verb}'")
                    score -= 0.1

            # Check for first-person pronouns
            if any(pronoun in text.lower() for pronoun in [" i ", " my ", " me "]):
                issues.append(f"{section_name}: Contains first-person pronouns")
                score -= 0.1

            # Check for excessive length
            word_count = len(text.split())
            if word_count > 500:
                issues.append(f"{section_name}: Excessive length ({word_count} words)")
                score -= 0.05

        result = {"quality_score": max(score, 0.0), "issues": issues, "passed": len(issues) == 0}

        if issues:
            self.record_fail(
                f"Quality issues found: {len(issues)}", data=result, signal="QUALITY_FAILURE"
            )
        else:
            self.record_pass("Content quality validated")

        return result
