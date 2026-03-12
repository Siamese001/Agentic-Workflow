"""
Weight Adjustment Engine - Dynamic section weight calibration
Refactored from adjust_section_weights.py
Following Batch 4 specifications

HARDENING: Reads 'ctx.signals' directly (Event-Driven). Reads/Writes 'weight_config' to Buffer.
"""
from __future__ import annotations
import logging
from typing import Any
from apps_rg.engines.base_rg_engine import BaseRGEngine
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
Logger = logging.getLogger(__name__)

class WeightAdjustmentEngine(BaseRGEngine):
    """
    Sovereign Refinement Engine.
    Reads: 'ctx.signals' (Implicit), 'section_weights' (Optional)
    Writes: 'adjusted_weights'
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id='REFINE.WEIGHTS')

    async def execute(self) -> dict[str, float]:
        """
        Calculate section weights based on active signals.
        """
        active_signals = self.ctx.signals
        adjustments = self._calculate_adjustments(active_signals)
        self.ctx.buffer.write('adjusted_weights', adjustments, source_agent=self.name)
        if adjustments:
            self.record_pass(f'Weights adjusted based on {len(active_signals)} signals')
        else:
            self.record_pass('No weight adjustments triggered')
        return adjustments

    def _calculate_adjustments(self, signals: set[str]) -> dict[str, float]:
        adjustments = {'default': 1.0}
        if 'ATS_FAILURE' in signals:
            adjustments['skills'] = 1.25
            adjustments['summary'] = 1.1
        if 'QUALITY_FAILURE' in signals:
            adjustments['experience'] = 1.3
        return adjustments
