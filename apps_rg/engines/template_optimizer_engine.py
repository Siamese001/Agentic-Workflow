"""
Template Optimizer Engine - Selects optimal presentation template
Refactored from RgTemplateOptimizerAgent.py
Following Batch 5 specifications

HARDENING: Reads 'mission_input' (JD). Selects visual strategy. Writes 'template_strategy'.
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

_emit_applies_guardrail("p0", "template_optimizer_engine", "p0_governance")
_emit_reads_policy_state("p0", "template_optimizer_engine", "policy_binding")
_emit_snapshots_state("p0", "template_optimizer_engine", "state_snapshot")
emit_replay_key("p0", "template_optimizer_engine")
emit_determinism_digest("p0", "template_optimizer_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class TemplateOptimizerEngine(BaseRGEngine):
    """
    Sovereign Refinement Engine.
    Reads: 'mission_input'
    Writes: 'template_strategy'
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.TEMPLATE")

    async def execute(self) -> dict[str, Any]:
        """
        Select presentation template based on JD analysis.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "TemplateOptimizerEngine.execute")

        mission = self.ctx.buffer.read("mission_input")
        jd_text = mission.get("job_description", "") if mission else ""
        if not jd_text:
            self.record_fail("Empty JD", signal="DATA_MISSING")
            return {"template": "standard"}
        job_type = self._detect_job_type(jd_text)
        result = {"job_type": job_type, "recommended_template": f"sov_v2_{job_type}"}
        self.ctx.buffer.write("template_strategy", result, source_agent=self.name)
        self.record_pass(f"Template selected: {job_type}")
        return result

    def _detect_job_type(self, text: str) -> str:
        if "manager" in text.lower() or "lead" in text.lower():
            return "executive"
        return "technical"
