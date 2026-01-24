"""
Weight Adjustment Engine - Dynamic section weight calibration
Refactored from adjust_section_weights.py
Following Batch 4 specifications

HARDENING: Reads 'ctx.signals' directly (Event-Driven). Reads/Writes 'weight_config' to Buffer.
"""

from __future__ import annotations
from typing import Any
import logging

from apps_rg.engines.base.base_resume_engine import BaseRGEngine

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
        # 1. READ Signals (Event-Driven Architecture)
        active_signals = self.ctx.signals

        # 2. LOGIC: Dynamic Adjustment
        adjustments = self._calculate_adjustments(active_signals)

        # 3. WRITE to Buffer
        # This allows downstream engines (Ranker, Generator) to read the adjusted weights
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
            adjustments["summary"] = 1.10
        if "QUALITY_FAILURE" in signals:
            adjustments["experience"] = 1.30
        return adjustments
