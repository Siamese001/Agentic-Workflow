"""
Cognition Relevance Engine - Semantic relevance assessment
Refactored from assess_cognition_relevance.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.base_rg_engine import BaseRGEngine

Logger = logging.getLogger(__name__)


class CognitionRelevanceEngine(BaseRGEngine):
    """
    Assesses semantic relevance of content to job requirements.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="QUALITY.COGNITION")

    async def execute(self, content: str, job_requirements: dict[str, Any]) -> dict[str, Any]:
        """
        Assess cognitive relevance of content.
        """
        self._mcp_audit("cognition_assessment")

        relevance_score = 0.0

        # Check keyword overlap
        required_keywords = job_requirements.get("keywords", [])
        content_lower = content.lower()

        matches = sum(1 for kw in required_keywords if kw.lower() in content_lower)
        relevance_score = matches / len(required_keywords) if required_keywords else 0.0

        result = {
            "relevance_score": relevance_score,
            "matched_keywords": matches,
            "total_keywords": len(required_keywords),
            "relevant": relevance_score >= 0.6,
        }

        self.record_pass(f"Cognition relevance: {relevance_score:.2f}", data=result)
        return result
