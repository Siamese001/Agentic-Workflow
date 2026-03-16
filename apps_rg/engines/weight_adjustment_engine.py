"""
Weight Adjustment Engine - Dynamic section weight calibration
Refactored from adjust_section_weights.py
Following Batch 4 specifications

HARDENING: Reads 'ctx.signals' directly (Event-Driven). Reads/Writes 'weight_config' to Buffer.
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

_emit_applies_guardrail("p0", "weight_adjustment_engine", "p0_governance")
_emit_reads_policy_state("p0", "weight_adjustment_engine", "policy_binding")
_emit_snapshots_state("p0", "weight_adjustment_engine", "state_snapshot")
emit_replay_key("p0", "weight_adjustment_engine")
emit_determinism_digest("p0", "weight_adjustment_engine")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class WeightAdjustmentEngine(BaseRGEngine):
    """
    Sovereign Refinement Engine.
    Reads: 'ctx.signals' (Implicit), 'section_weights' (Optional)
    Writes: 'adjusted_weights'
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.WEIGHTS")

    async def execute(self) -> dict[str, float]:
        """
        Calculate section weights based on active signals.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "WeightAdjustmentEngine.execute")

        active_signals = self.ctx.signals
        adjustments = self._calculate_adjustments(active_signals)
        self.ctx.buffer.write("adjusted_weights", adjustments, source_agent=self.name)
        if adjustments:
            self.record_pass(f"Weights adjusted based on {len(active_signals)} signals")
        else:
            self.record_pass("No weight adjustments triggered")
        return adjustments

    def _calculate_adjustments(self, signals: set[str]) -> dict[str, float]:
        adjustments = {"default": 1.0}
        if "ATS_FAILURE" in signals:
            adjustments["skills"] = 1.25
            adjustments["summary"] = 1.1
        if "QUALITY_FAILURE" in signals:
            adjustments["experience"] = 1.3
        return adjustments
