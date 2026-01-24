"""
Fact Check Engine - Hallucination prevention
Refactored from FactCheckAgent.py
"""

from __future__ import annotations
from typing import Any, Dict, List
import logging

from apps_rg.engines.base.base_resume_engine import BaseRGEngine

Logger = logging.getLogger(__name__)


class FactCheckEngine(BaseRGEngine):
    """
    Validates factual accuracy and prevents hallucinations.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="SAFETY.FACT_CHECK")

    async def execute(self, claims: List[str], source_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify claims against source data.
        """
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
            "verification_rate": len(verified_claims) / len(claims) if claims else 1.0
        }
        
        if result["verification_rate"] < 0.8:
            self.record_fail(f"Low verification rate: {result['verification_rate']:.1%}", data=result, signal="FACT_CHECK_FAILURE")
        else:
            self.record_pass(f"Fact check passed: {result['verification_rate']:.1%} verified")
        
        return result
    
    def _verify_claim(self, claim: str, source: Dict[str, Any]) -> bool:
        """Verify single claim against source."""
        # Simplified verification - in production would use semantic matching
        source_text = str(source).lower()
        claim_lower = claim.lower()
        
        # Check if key terms from claim appear in source
        claim_words = set(claim_lower.split())
        source_words = set(source_text.split())
        
        overlap = len(claim_words & source_words)
        return overlap >= len(claim_words) * 0.5
