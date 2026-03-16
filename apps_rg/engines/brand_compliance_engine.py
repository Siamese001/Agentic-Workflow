"""
Brand Compliance Engine - Tone policing
Refactored from BrandComplianceAgent.py
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

_emit_applies_guardrail("p0", "brand_compliance_engine", "p0_governance")
_emit_reads_policy_state("p0", "brand_compliance_engine", "policy_binding")
_emit_snapshots_state("p0", "brand_compliance_engine", "state_snapshot")
emit_replay_key("p0", "brand_compliance_engine")
emit_determinism_digest("p0", "brand_compliance_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "BrandComplianceEngine.execute")

        self._mcp_audit("brand_compliance_check")
        violations = []
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
                f"Brand compliance violations: {len(violations)}", data=result, signal="BRAND_VIOLATION"
            )
        else:
            self.record_pass("Brand compliance validated")
        return result
