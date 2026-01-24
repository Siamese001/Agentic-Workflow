"""
Weight Adjustment Engine - Dynamic section weight calibration
Refactored from adjust_section_weights.py
Following Batch 4 specifications
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional
import logging

from apps_rg.engines.base.base_resume_engine import BaseRGEngine

Logger = logging.getLogger(__name__)


class WeightAdjustmentEngine(BaseRGEngine):
    """
    Sovereign Refinement Engine.
    Dynamically adjusts section weights based on JD alignment signals.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="REFINE.WEIGHTS")
        # Default weights from self.thresholds['default_weights']

    async def execute(self, section_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply dynamic weighting to resume sections.
        """
        self._mcp_audit("weight_adjustment_start")
        
        # 1. Detection: Check for specific failures in the context
        active_signals = getattr(self.ctx, 'signals', set())
        adjustments = self._calculate_adjustments(active_signals)
        
        # 2. Refine input data (Ported from AdjustSectionWeights.py)
        refined_sections = {}
        changes = []
        
        for section, content in section_data.items():
            weight = adjustments.get(section, 1.0)
            if weight != 1.0:
                changes.append(f"{section}: weight adjusted to {weight}")
            
            refined_sections[section] = {
                "content": content,
                "applied_weight": weight
            }

        if not changes:
            self.record_pass("No weight adjustments required for current state")
        else:
            self.record_pass(f"Applied {len(changes)} weight adjustments", data={"changes": changes})

        return refined_sections

    def _calculate_adjustments(self, signals: set) -> Dict[str, float]:
        """Determine weight shifts based on L3 signals."""
        adjustments = {}
        
        # Logic from LIC Standard: If ATS fails, increase keyword-heavy section weights
        if "ATS_FAILURE" in signals:
            adjustments["skills"] = 1.25
            adjustments["summary"] = 1.10
            
        # If Quality fails, prioritize experience validation
        if "QUALITY_FAILURE" in signals:
            adjustments["experience"] = 1.30
            
        return adjustments
