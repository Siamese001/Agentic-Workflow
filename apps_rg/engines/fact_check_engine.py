"""
Fact Check Engine - Hallucination prevention
Refactored from FactCheckAgent.py
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

_emit_applies_guardrail("p0", "fact_check_engine", "p0_governance")
_emit_reads_policy_state("p0", "fact_check_engine", "policy_binding")
_emit_snapshots_state("p0", "fact_check_engine", "state_snapshot")
emit_replay_key("p0", "fact_check_engine")
emit_determinism_digest("p0", "fact_check_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
