"""
Fact Check Engine - Hallucination prevention
Refactored from FactCheckAgent.py
"""

from __future__ import annotations

import logging
from typing import Any

from apps_rg.engines.base_rg_engine import BaseRGEngine
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

Logger = logging.getLogger(__name__)


class FactCheckEngine(BaseRGEngine):
    """
    Validates factual accuracy and prevents hallucinations.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="SAFETY.FACT_CHECK")

    async def execute(self, claims: list[str], source_data: dict[str, Any]) -> dict[str, Any]:
        """
        Verify claims against source data.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "FactCheckEngine.execute")

        self._mcp_audit("fact_check_start", {"claim_count": len(claims)})
        verified_claims = []
        unverified_claims = []
        for claim in claims:
            if self._verify_claim(claim, source_data):
                verified_claims.append(claim)
            else:
                unverified_claims.append(claim)
        result = {
            "verified_count": len(verified_claims),
            "unverified_count": len(unverified_claims),
            "unverified_claims": unverified_claims,
            "verification_rate": len(verified_claims) / len(claims) if claims else 1.0,
        }
        if result["verification_rate"] < 0.8:
            self.record_fail(
                f"Low verification rate: {result['verification_rate']:.1%}",
                data=result,
                signal="FACT_CHECK_FAILURE",
            )
        else:
            self.record_pass(f"Fact check passed: {result['verification_rate']:.1%} verified")
        return result

    def _verify_claim(self, claim: str, source: dict[str, Any]) -> bool:
        """Verify single claim against source."""
        source_text = str(source).lower()
        claim_lower = claim.lower()
        claim_words = set(claim_lower.split())
        source_words = set(source_text.split())
        overlap = len(claim_words & source_words)
        return overlap >= len(claim_words) * 0.5
