"""
Cognition Relevance Engine - Semantic relevance assessment
Refactored from assess_cognition_relevance.py
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

_emit_applies_guardrail("p0", "cognition_relevance_engine", "p0_governance")
_emit_reads_policy_state("p0", "cognition_relevance_engine", "policy_binding")
_emit_snapshots_state("p0", "cognition_relevance_engine", "state_snapshot")
emit_replay_key("p0", "cognition_relevance_engine")
emit_determinism_digest("p0", "cognition_relevance_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "CognitionRelevanceEngine.execute")

        self._mcp_audit("cognition_assessment")
        relevance_score = 0.0
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
