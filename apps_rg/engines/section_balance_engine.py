"""
Section Balance Engine - Length/ratio validation
Refactored from SectionBalanceAgent.py
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

_emit_applies_guardrail("p0", "section_balance_engine", "p0_governance")
_emit_reads_policy_state("p0", "section_balance_engine", "policy_binding")
_emit_snapshots_state("p0", "section_balance_engine", "state_snapshot")
emit_replay_key("p0", "section_balance_engine")
emit_determinism_digest("p0", "section_balance_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class SectionBalanceEngine(BaseRGEngine):
    """
    Validates section length and ratio balance.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.BALANCE")

    async def execute(self, sections: dict[str, Any]) -> dict[str, Any]:
        """
        Validate section balance and ratios.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SectionBalanceEngine.execute")

        self._mcp_audit("balance_check")
        section_lengths = {}
        for name, content in sections.items():
            if isinstance(content, str):
                section_lengths[name] = len(content.split())
            elif isinstance(content, list):
                section_lengths[name] = sum(len(str(item).split()) for item in content)
        total_words = sum(section_lengths.values())
        ratios = {name: length / total_words for name, length in section_lengths.items()}
        issues = []
        exp_ratio = ratios.get("experience", 0)
        if exp_ratio < 0.4 or exp_ratio > 0.6:
            issues.append(f"Experience ratio {exp_ratio:.1%} outside target 40-60%")
        summary_ratio = ratios.get("summary", 0)
        if summary_ratio > 0.2:
            issues.append(f"Summary ratio {summary_ratio:.1%} exceeds 20% limit")
        result = {
            "balanced": len(issues) == 0,
            "section_lengths": section_lengths,
            "ratios": ratios,
            "issues": issues,
        }
        if issues:
            self.record_fail("Section balance issues detected", data=result, signal="BALANCE_VIOLATION")
        else:
            self.record_pass("Section balance validated")
        return result
